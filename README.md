# smoked mirrors
Learn how to spot python bugs, LLM powered.

## Running
```
git clone https://github.com/Pseudoleon/smoked-mirrors.git
cd smoked-mirrors
python -m venv venv
. venv/bin/activate
pip install -r requirements.txt
```
If you use other shells (e.g. powershell, fish..) use the appopriate venv `activate` script. Then to run just do:
```
python server.py
```

## How it works
LLama2 (llamaapi) is used to generate buggy code based on the topic you want to practice. The code is then run inside a sandbox and checked. Click on the line which causes the first crash! It can be at compile-time or run-time.

## Security
May be susceptible to template injection and sandbox escape via prompt engineering. Running inside a container is recommended.

## Contribution
Website layout forked from: https://github.com/jgoney/flask-messenger