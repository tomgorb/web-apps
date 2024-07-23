# web-based apps

## flask

```bash
pip install -r requirements.txt
python server.py
```

```python
>>> import importlib
>>> importlib.metadata.version("flask")
'3.0.3'
```


## gradio

```bash
python app.py
```

```python
>>> import gradio
>>> gradio.__version__
'4.36.1'
```


## streamlit

```bash
streamlit run app.py
```

```python
>>> import streamlit
>>> streamlit.__version__
'1.35.0'
```

### data

- *geo.csv*: mock data from [Mockaroo](https://www.mockaroo.com/)
- *web.csv*: some user generated data *Google Analytics* style