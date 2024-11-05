python -m venv venv && ^
venv\Scripts\activate.bat && ^
python.exe -m pip install --upgrade pip && ^
python.exe -m pip install --upgrade build && ^
python.exe -m pip install --upgrade setuptools && ^
python.exe -m pip install -r requirements.txt && ^
python.exe -m pip install -e .

cmd /k