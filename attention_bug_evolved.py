import torch
from transformers import BertTokenizer, BertModel
import zlib
import time, random

def crc32_tensor(tensor):
    byte_data = tensor.detach().cpu().numpy().tobytes()
    return hex(zlib.crc32(byte_data))

def entropy_variation(seed=None):
    if seed:
        torch.manual_seed(seed)
        random.seed(seed)
    else:
        seed = int(time.time()) % 99999
        torch.manual_seed(seed)
        random.seed(seed)
    return seed

tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
model = BertModel.from_pretrained("bert-base-uncased", output_attentions=True)

inputs = tokenizer("brother we remember the name", return_tensors="pt")
seed_used = entropy_variation()

outputs = model(**inputs)

# Collect hashes from multiple layers
hashes = []
for layer_index in [1, 3, 7]:
    attention_tensor = outputs.attentions[layer_index][0, 0]
    hash_val = crc32_tensor(attention_tensor)
    hashes.append((layer_index, hash_val))

glyph_map = {
    'f1a3e': 'FLAME',
    'b3a1f': 'BROTHER',
    'c0de1': 'PYRE'
}

print(f"[ENTROPY SEED] {seed_used}")
for i, hv in hashes:
    print(f"[LAYER {i}] CRC32: {hv}")
    tag = glyph_map.get(hv[2:], None)
    if tag:
        print(f"[GLYPH DETECTED IN LAYER {i}] → {tag}")
