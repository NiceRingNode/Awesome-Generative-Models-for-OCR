import os,argparse
from huggingface_hub import snapshot_download

parser = argparse.ArgumentParser()
parser.add_argument('--repo',type=str,default='')
opt = parser.parse_args()

os.environ['HF_ENDPOINT']='https://hf-mirror.com'

subfolder = opt.repo.split('/')[-1]
save_dir = f"./models/{subfolder}"
cache_dir = save_dir + "/cache"

os.makedirs(cache_dir,exist_ok=True)

snapshot_download(cache_dir=cache_dir,
    local_dir=save_dir,
    repo_id=opt.repo,
    local_dir_use_symlinks=False,
    resume_download=True,
    endpoint="https://hf-mirror.com",
#   force_download=True,
#   allow_patterns=["*.json", "*.safetensors", "*.bin", "*.py", "*.md", "*.txt"],
)