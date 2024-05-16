## Demo video link" https://www.loom.com/share/9ab447ab84814e2ba1a1c9926701d777

## For any queries email at: mohibovais79@gmail.com

# bleed-ai
Python Developer Technical Assessment


# FastAPI Application

## Setup and Installation

### Conda Environment
1. Clone this repository.
2. Install Conda.
3. Create and activate a new Conda environment:

Run these commands to  activate conda environment with all libraries installed

   ```
conda env create -f environment.yml
conda activate myenv
```
# Alternatively if you only want the required libraries  run this command:

```
pip install -r requirements.txt
```
# After downloading dependencies run this command to run the application:

```
uvicorn app:app --reload
```

# Running with Docker

1. Install Docker.
2. Run the following command to build and start the application:

```
docker build -t bleed-ai .

docker run -p 8000:8000 bleed-ai

```


