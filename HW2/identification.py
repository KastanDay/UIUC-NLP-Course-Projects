import json
import re

import numpy as np
import tqdm
from openprompt.data_utils import InputExample, InputFeatures
from openprompt.plms import load_plm
from torch.utils.data._utils.collate import default_collate


def save_div(a, b):
    if b != 0:
        return a / b
    else:
        return 0.0


def evaluation(gold_labels, pred_labels, vocab):
    inv_vocab = {v:k for k,v in vocab.items()}
    result = {}
    for label, idx in vocab.items():
        if idx != 0:
            result[label] = {"prec": 0.0, "rec": 0.0, "f1": 0.0}

    total_pred_num, total_gold_num, total_correct_num = 0.0, 0.0, 0.0

    for i in range(len(gold_labels)):
        pred_labels_i = pred_labels[i]
        gold_labels_i = gold_labels[i]

        for idx in gold_labels_i:
            if idx != 0:
                total_gold_num += 1
                result[inv_vocab[idx]]["rec"] += 1

        for idx in pred_labels_i:
            if idx != 0:
                total_pred_num += 1
                result[inv_vocab[idx]]["prec"] += 1

                if idx in gold_labels_i:
                    total_correct_num += 1
                    result[inv_vocab[idx]]["f1"] += 1

    for label in result:
        counts = result[label]
        counts["prec"] = save_div(counts["f1"], counts["prec"])
        counts["rec"] = save_div(counts["f1"], counts["rec"])
        counts["f1"] = save_div(2*counts["prec"]*counts["rec"], counts["prec"]+counts["rec"])

    prec = save_div(total_correct_num, total_pred_num)
    rec = save_div(total_correct_num, total_gold_num)
    f1 = save_div(2*prec*rec, prec+rec)

    return prec, rec, f1, result


def load_data(input_dir):
    data_items = []

    with open(input_dir, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    for line in lines:
        item = json.loads(line)
        data_items.append(item)
    return data_items


def get_vocab(train_dir, valid_dir):
    train_data = load_data(train_dir)
    valid_data = load_data(valid_dir)
    vocab = {"None": 0}

    for item in train_data:
        for event in item["events"]:
            if event[-1] not in vocab:
                vocab[event[-1]] = len(vocab)

    for item in valid_data:
        for event in item["events"]:
            if event[-1] not in vocab:
                vocab[event[-1]] = len(vocab)

    return vocab


def process_data(input_dir, vocab):
    items = load_data(input_dir)
    output_items = []

    for i,item in enumerate(items):
        labels = []

        for event in item["events"]:
            if vocab[event[-1]] not in labels:
                labels.append(vocab[event[-1]])

        if len(labels) == 0:
            labels.append(0)

        input_example = InputExample(text_a=" ".join(item["tokens"]), label=labels, guid=i)
        output_items.append(input_example)

    return output_items


def my_collate_fn(batch):
    elem = batch[0]
    return_dict = {}
    for key in elem:
        if key == "encoded_tgt_text":
            return_dict[key] = [d[key] for d in batch]
        else:
            try:
                return_dict[key] = default_collate([d[key] for d in batch])
            except:
                return_dict[key] = [d[key] for d in batch]

    return InputFeatures(**return_dict)


def convert_labels_to_list(labels):
    label_list = []
    for label in labels:
        label_list.append(label.tolist().copy())
    return label_list


def to_device(data, device):
    for key in ["input_ids", "attention_mask", "decoder_input_ids", "loss_ids"]:
        data[key] = data[key].to(device)
    return data


def get_plm():
    # You may change the PLM you'd like to use. Currently it's t5-base.
    return load_plm("t5", "t5-base")

def get_template():
    # You may design your own template here.
    return '{"placeholder":"text_a"} This text describes a {"mask"} event.'

def get_verbalizer(vocab):
    # Input: a dictionary for event types to indices: e.g.: {'None': 0, 'Catastrophe': 1, 'Causation': 2, 'Motion': 3, 'Hostile_encounter': 4, 'Process_start': 5, 'Attack': 6, 'Killing': 7, 'Conquering': 8, 'Social_event': 9, 'Competition': 10}

    # Output: A 2-dim list. Verbalizers for each event type. Currently this function directly returns the lowercase for each event type name (and the performance is low). You may want to design your own verbalizers to improve the performance.

    return [[label.lower()] for label in vocab]


def loss_func(logits, labels):

    # INPUT:
    ##  logits: a torch.Tensor of (batch_size, number_of_event_types) which is the output logits for each event type (none types are included).
    ##  labels: a 2-dim List which denotes the ground-truth labels for each sentence in the batch. Note that there cound be multiple events, a single event, or no events for each sentence.
    ##  For example, if labels == [[0], [2,3,4]] then the batch size is 2 and the first sentence has no events, and the second sentence has three events of indices 2,3 and 4.

    ##  INSTRUCTIONS: In general, we want to maximize the logits of correct labels and minimize the logits with incorrect labels. You can implement your own loss function here or you can refer to what loss function is used in https://arxiv.org/pdf/2202.07615.pdf

    ## OUTPUT:
    ##   The output should be a pytorch scalar --- the loss.

    ###  YOU NEED TO WRITE YOUR CODE HERE.  ###

    negative_loss_total = torch.zeros(logits.shape[0])
    positive_loss_total = torch.zeros(logits.shape[0])

    for i in range(len(labels)):
      negative_loss = positive_loss = 0
      for inner_itr in range(logits.shape[1]):
        if inner_itr in labels[i]:
          positive_loss += torch.log( torch.exp(logits[i][inner_itr]) / (torch.exp(logits[i][inner_itr]) + torch.exp(logits[i][0])) )
        elif inner_itr != 0:
          negative_loss += torch.exp( logits[i][inner_itr] )

      positive_loss_total[i] = positive_loss/(len(labels[i]))
      negative_loss_total[i] = torch.log( torch.exp( logits[i][0] ) / (torch.exp( logits[i][0] ) + negative_loss) )

    # multiple by -1 to make it a maximized value for this problem (unlike how PyTorch will typically minimize)
    return torch.mean( negative_loss_total + positive_loss_total ) * -1


def predictions_to_proper_format(predicted_vocab_indexes):
  """ 
  Go from a list of lists of vocab indexes to a list of lists of event types. As the grading requires. 
  """
  formatted_predictions = []
  for vocab_index_batch in predicted_vocab_indexes:
    batch_vocab = []
    for vocab_index in vocab_index_batch:
      if vocab_index == 0:
        break
      batch_vocab.append(inv_vocabulary[vocab_index])
    formatted_predictions.append({'predictions': batch_vocab})
  return formatted_predictions    


def predict(logits):
    # INPUT:
    ##  logits: a torch.Tensor of (batch_size, number_of_event_types) which is the output logits for each event type (none types are included).
    # OUTPUT:
    ##  a 2-dim list which has the same format with the "labels" in "loss_func" --- the predictions for all the sentences in the batch.
    ##  For example, if predictions == [[0], [2,3,4]] then the batch size is 2, and we predict no events for the first sentence and three events (2,3,and 4) for the second sentence.

    ##  INSTRUCTIONS: The most straight-forward way for prediction is to select out the indices with maximum of logits. Note that this is a multi-label classification problem, so each sentence could have multiple predicted event indices. Using what threshold for prediction is important here. You can also use the None event (index 0) as the threshold as what https://arxiv.org/pdf/2202.07615.pdf does.

    ###  YOU NEED TO WRITE YOUR CODE HERE.  ###
    # print(logits.shape)
    # print(logits)

    pred = []
    for logit in logits:
        # pred.append([0])
        labels = logits = []
        null_pred_logit = logit[0]
        for i, inner_logit in enumerate(logit):
          if inner_logit > null_pred_logit:
            labels.append(i)
        # no good predictions, just predict null (my doode)
        if not labels:
          labels.append(0)
        pred.append(labels)
    return pred

if __name__ == "__main__":
    train_dir = "./data/train.json"
    valid_dir = "./data/valid.json"
    test_dir = "./data/test.json"

    vocabulary = get_vocab(train_dir, valid_dir)
    dataset = {
        "train": process_data(train_dir, vocabulary),
        "validation": process_data(valid_dir, vocabulary),
        "test": process_data(test_dir, vocabulary)
    }
    # print(vocabulary)
    inv_vocabulary = {v:k for k,v in vocabulary.items()}
    print("HERE IS THAT KEY VOCAB")
    print(inv_vocabulary)

    from openprompt.prompts import ManualTemplate
    plm, tokenizer, model_config, WrapperClass = get_plm()

    template_text = get_template()
    mytemplate = ManualTemplate(tokenizer=tokenizer, text=template_text)

    from openprompt import PromptDataLoader
    train_dataloader = PromptDataLoader(
        dataset=dataset["train"],
        template=mytemplate,
        tokenizer=tokenizer,
        tokenizer_wrapper_class=WrapperClass,
        max_seq_length=256,
        decoder_max_length=3,
        batch_size=10,
        shuffle=True,
        teacher_forcing=False,
        predict_eos_token=False,
        truncate_method="head"
    )
    train_dataloader.dataloader.collate_fn = my_collate_fn

    validation_dataloader = PromptDataLoader(
        dataset=dataset["validation"],
        template=mytemplate,
        tokenizer=tokenizer,
        tokenizer_wrapper_class=WrapperClass,
        max_seq_length=256,
        decoder_max_length=3,
        batch_size=10,
        shuffle=False,
        teacher_forcing=False,
        predict_eos_token=False,
        truncate_method="head"
    )
    validation_dataloader.dataloader.collate_fn = my_collate_fn

    test_dataloader = PromptDataLoader(
        dataset=dataset["test"],
        template=mytemplate,
        tokenizer=tokenizer,
        tokenizer_wrapper_class=WrapperClass,
        max_seq_length=256,
        decoder_max_length=3,
        batch_size=10,
        shuffle=False,
        teacher_forcing=False,
        predict_eos_token=False,
        truncate_method="head"
    )
    test_dataloader.dataloader.collate_fn = my_collate_fn

    import torch
    from openprompt.prompts import ManualVerbalizer

    label_words = get_verbalizer(vocabulary)
    # for example the verbalizer contains multiple label words in each class
    myverbalizer = ManualVerbalizer(tokenizer,
        num_classes=len(vocabulary),
        label_words=label_words
    )

    from openprompt import PromptForClassification
    use_cuda = True
    prompt_model = PromptForClassification(plm=plm, template=mytemplate, verbalizer=myverbalizer, freeze_plm=False)
    if use_cuda:
        prompt_model = prompt_model.cuda()

    from transformers import AdamW, get_linear_schedule_with_warmup
    no_decay = ['bias', 'LayerNorm.weight']
    # it's always good practice to set no decay to biase and LayerNorm parameters
    optimizer_grouped_parameters = [
        {'params': [p for n, p in prompt_model.named_parameters() if not any(nd in n for nd in no_decay)], 'weight_decay': 0.01},
        {'params': [p for n, p in prompt_model.named_parameters() if any(nd in n for nd in no_decay)], 'weight_decay': 0.0}
    ]
    optimizer = AdamW(optimizer_grouped_parameters, lr=1e-4)

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print("device:", device)

    max_f1 = 0.0
    max_patience, current_patience = 3, 0
    if_exit = False

    for epoch in range(10):
        if if_exit:
            break
        tot_loss = 0.0
        progress = tqdm.tqdm(total=len(train_dataloader), ncols=150, desc="Epoch: "+str(epoch))
        for step, inputs in enumerate(train_dataloader):
            if if_exit:
                break
            if use_cuda:
                inputs = to_device(inputs, device)
            logits = prompt_model(inputs)
            labels = inputs['label']
            label_list = convert_labels_to_list(labels)
            loss = loss_func(logits, label_list)
            loss.backward()
            tot_loss += loss.item()
            optimizer.step()
            optimizer.zero_grad()

            if step %100 ==99:
                print("\nStep {}, average loss: {}".format(step, tot_loss/(step+1)), flush=True)

                allpreds, alllabels = [], []
                # Validation:
                valid_progress = tqdm.tqdm(total=len(validation_dataloader), ncols=150, desc="Validation: ")
                prompt_model.eval()
                with torch.no_grad():
                    for step, inputs in enumerate(validation_dataloader):
                        if use_cuda:
                            inputs = to_device(inputs, device)
                        logits = prompt_model(inputs)
                        labels = inputs['label']
                        label_list = convert_labels_to_list(labels)
                        pred_labels = predict(logits)

                        # KASTAN CODE HERE


                        alllabels.extend(label_list)
                        allpreds.extend(pred_labels)
                        valid_progress.update(1)

                valid_progress.close()
                prompt_model.train()

                p, r, f, total = evaluation(alllabels, allpreds, vocabulary)
                print("F1-Score: " + str(f))
                with open("results.json", 'w', encoding='utf-8') as f_out:
                    f_out.write(json.dumps(total, indent=4))
                if f > max_f1:
                    max_f1 = f
                    torch.save(prompt_model.state_dict(), "./checkpoint_best.pt")
                    current_patience = 0
                else:
                    current_patience += 1
                    if current_patience > max_patience:
                        if_exit = True


            progress.update(1)
        progress.close()



    ### Dumped out the results for test dataset.

    ### You need to write your code here to dump out the dataset using "test_dataloader".
    ### you need to write out all your model predictions into a file "output.json".
    ### Each line of the "output.json" is the model prediction for the sentence.

    ### You may find "inv_vocabulary" useful here.

    ### Each line should be in the following format:
    ###    {"predictions": ["Catastrophe", "Conquering"]}
    ###    {"predictions": ["Social_event"]}
    ###    {"predictions": []}

    ### Note that the sentence order for your output file should be the same with the original file!

    final_predictions = []
    for idx, inputs in enumerate(test_dataloader):
      inputs = inputs.to(device)
      logits = prompt_model(inputs)
      final_predictions.extend(predictions_to_proper_format(predict(logits)))
    # print(final_predictions)

    import json
    json_object = json.dumps(final_predictions, indent=4)
    with open("output.json", "w") as outfile:
      outfile.write(json_object)
