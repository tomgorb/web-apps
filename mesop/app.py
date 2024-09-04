import re
import time
import base64

import mesop as me
import numpy as np
import pandas as pd

from datetime import datetime

from matplotlib.figure import Figure
import matplotlib.ticker as mtick

###############
# STATE CLASS #
###############
@me.stateclass
class State:
  # CHEAT SHEET
  res: str
  clicks: int
  checked: bool
  text: str
  radio_value: str
  selected_values: list[str]
  toggled: bool = False
  initial_input_value: str = "50.0"
  initial_slider_value: float = 50.0
  slider_value: float = 50.0
  file: me.UploadedFile
  selected_cell: str = "No cell selected."
  raw_value: str
  selected_value: str
  #
  input: str
  output: str
  render: bool
  # df: pd.DataFrame
  identifier: str
  column: str
###############

@me.page(path="/")
def page():
  with me.box(
    style=me.Style(
      background="#fff",
      min_height="calc(100% - 48px)",
      padding=me.Padding(bottom=16),
    )
  ):
    with me.box(
      style=me.Style(
        width="min(720px, 100%)",
        margin=me.Margin.symmetric(horizontal="auto"),
        padding=me.Padding.symmetric(
          horizontal=16,
        ),
      )
    ):
      header_text()
      example_row()
      input()
      output()
    
  footer()

def header_text():
  with me.box(
    style=me.Style(
      padding=me.Padding(
        top=64,
        bottom=36,
      ),
    )
  ):
    me.text(
      "Mesop",
      style=me.Style(
        font_size=36,
        font_weight=700,
        background="linear-gradient(90deg, #4285F4, #AA5CDB, #DB4437) text",
        color="transparent",
      ),
    )

EXAMPLES = [
  "Plot web data",
  "Cheat sheet",
]

def example_row():
  is_mobile = me.viewport_size().width < 640
  with me.box(
    style=me.Style(
      display="flex",
      flex_direction="column" if is_mobile else "row",
      gap=48,
      margin=me.Margin(bottom=36),
    )
  ):
    for example in EXAMPLES:
      example_box(example, is_mobile)

def example_box(example: str, is_mobile: bool):
  with me.box(
    style=me.Style(
      width="100%" if is_mobile else 200,
      background="#F0F4F9",
      padding=me.Padding.all(16),
      font_weight=500,
      text_align="center",
      line_height="5",
      border_radius=16,
      cursor="pointer",
    ),
    key=example,
    on_click=click_example_box,
  ):
    me.text(example)

def click_example_box(e: me.ClickEvent):
  state = me.state(State)
  state.input = e.key
  state.output = None
  state.render = False

def input():
  state = me.state(State)
  with me.box(
    style=me.Style(
      padding=me.Padding.all(8),
      background="white",
      display="flex",
      width="100%",
      border=me.Border.all(
        me.BorderSide(width=0, style="solid", color="black")
      ),
      border_radius=12,
      box_shadow="0 10px 20px #0000000a, 0 2px 6px #0000000a, 0 0 1px #0000000a",
    )
  ):
    with me.box(
      style=me.Style(
        flex_grow=1,
      )
    ):
      me.native_textarea(
        value=state.input,
        autosize=True,
        min_rows=2,
        placeholder="",
        style=me.Style(
          padding=me.Padding(top=16, left=16),
          background="white",
          outline="none",
          width="100%",
          overflow_y="auto",
          border=me.Border.all(
            me.BorderSide(style="none"),
          ),
        ),
        on_blur=textarea_on_blur,
      )
    with me.content_button(type="icon", on_click=click_send):
      me.icon("send")

def textarea_on_blur(e: me.InputBlurEvent):
  state = me.state(State)
  state.input = e.value

def click_send(e: me.ClickEvent):
  state = me.state(State)
  if not state.input:
    return
  input = state.input
  state.output=None
  state.render=False

  if input == "Cheat sheet":
    navigate(e)

  else:
    state.output="Done"

def output():
  state = me.state(State)
  if state.output:
   
    with me.box(
      style=me.Style(
        background="#F0F4F9",
        padding=me.Padding.all(16),
        border_radius=16,
        margin=me.Margin(top=36),
      )
    ):

      res = load_data("web")
      id = list(res.identifier.unique())
      cols = list(res.columns)
      cols.remove("identifier")

      options=[me.RadioOption(label=str(x), value=str(x)) for x in id]
      with me.box():
        me.text("Select identifier")
        me.radio(on_change=radio_id,
          options=options,
          value=state.identifier)

      options=[me.RadioOption(label=str(x), value=str(x)) for x in cols]
      with me.box():
        me.text("Select column")
        me.radio(on_change=radio_col,
          options=options,
          value=state.column)

      with me.content_button(type="icon", on_click=on_click):
        me.icon("graphic_eq")

      if state.render and (state.identifier and state.column):
        for date in pd.date_range(start = res.index[0], end = res.index[-1],freq = '1W'):
            fig = plot_web(res, date, int(state.identifier), state.column)
        me.plot(fig, style=me.Style(width="100%"))

def on_click(e: me.ClickEvent):
  state = me.state(State)
  state.render=True

def radio_id(event: me.RadioChangeEvent):
  s = me.state(State)
  s.identifier = event.value
  s.render=False

def radio_col(event: me.RadioChangeEvent):
  s = me.state(State)
  s.column = event.value
  s.render=False

def footer():
  with me.box(
    style=me.Style(
      position="sticky",
      bottom=0,
      padding=me.Padding.symmetric(vertical=16, horizontal=16),
      width="100%",
      background="#F0F4F9",
      font_size=14,
    )
  ):
    me.html(
      "Made with <a href='https://google.github.io/mesop/'>Mesop</a>",
    )

def load_data(input):

  df = pd.read_csv("../data/%s.csv"%input, sep="|")

  if input=="web":
    cols_to_drop = [col for col in df.columns if re.search('visit', col)]
    df.drop(cols_to_drop, axis=1, inplace=True)
    df['day']=pd.to_datetime(df['day'])
    df.set_index(['day'],drop=True, inplace=True)
    df=df.groupby('identifier').resample('W').sum()
    return df.drop('identifier', axis=1).reset_index(0)

def plot_web(df,date,identifier,col):
  
  df = df[(df.identifier==identifier)]
  maxi1=round(df[col].max()*1.5)
  
  df=df.loc[df.index[0]:pd.Timestamp(date)]
  fig = Figure(dpi=100)
  ax1 = fig.subplots(1)
  ax1.plot(df[col],marker='o', linestyle='--', linewidth=2,markersize=3, color='tab:green')

  ax1.set_ylim([0, maxi1])
  ax1.tick_params(axis='x', labelsize=7)
  ax1.tick_params(axis='y', labelsize=7 , rotation=33)    
  ax1.yaxis.set_major_formatter(mtick.FormatStrFormatter('%.0e'))

  fig.suptitle('%s per week for identifier %s'%(col, identifier), fontsize=11)
  fig.tight_layout()
  return fig

def navigate(e: me.ClickEvent):
  me.navigate("/cheat-sheet")


# ===========
# CHEAT SHEET
# ===========

@me.page(path="/cheat-sheet")
def main():

    with me.box(
      style=me.Style(
        display="grid", grid_template_columns="1fr 2fr",
        gap=17,
        padding=me.Padding(left=36),
        margin=me.Margin(top=36, bottom=36)
      )
    ):

        s = me.state(State)

        #API CALL
        with me.box():
          me.button("API call", on_click=call, type="raised")
        with me.box():
          me.text(s.res)

        #COUNTER
        with me.box():
          me.button("Increment", on_click=counter, type="raised")
        with me.box():
          me.text(f"Clicks: {s.clicks}")

        #BUTTON
        with me.box():
          me.text("Button types:")
        with me.box(
          style=me.Style(
            display="flex", 
            flex_direction="row", 
            gap=12
          )
        ):
          me.button("default")
          me.button("raised", type="raised")
          me.button("flat", type="flat")
          me.button("stroked", type="stroked")

        with me.box():
          me.text("Button colors:")
        with me.box(
          style=me.Style(
            display="flex", 
            flex_direction="row", 
            gap=12
          )
        ):
          me.button("default", type="flat")
          me.button("primary", color="primary", type="flat")
          me.button("secondary", color="accent", type="flat")
          me.button("warn", color="warn", type="flat")

        #CHECKBOX
        with me.box():
          me.checkbox("Simple checkbox", on_change=checkbox)

        with me.box():
          if s.checked:
            me.text(text="is checked")
          else:
            me.text(text="is not checked")

        #TEXT INPUT
        with me.box():
          me.input(label="Basic input", on_blur=text)
        with me.box():
          me.text(text=s.text)

        #RADIO BOX
        with me.box():
          me.text("Horizontal radio options")
          me.radio(on_change=radio,
            options=[
              me.RadioOption(label="Option 1", value="1"),
              me.RadioOption(label="Option 2", value="2"),
            ],
            value=s.radio_value)
        me.text(text="Selected radio value: " + s.radio_value)

        #SELECT BOX
        with me.box():
          me.text(text="Select")
          me.select(label="Select",
            options=[
              me.SelectOption(label="label 1", value="value1"),
              me.SelectOption(label="label 2", value="value2"),
              me.SelectOption(label="label 3", value="value3"),
            ],
            on_selection_change=select,
            style=me.Style(width=500),
            multiple=True)
        with me.box():
          me.text(text="Selected values: " + ", ".join(s.selected_values))

        #TOOGLE
        with me.box():
          me.slide_toggle(label="Slide toggle", on_change=toogle)
        with me.box():
          me.text(text=f"Toggled: {s.toggled}")

        #SLIDER
        with me.box(
          style=me.Style(
            display="flex", 
            flex_direction="row"
          )
        ):
          me.input(label="Slider value", value=s.initial_input_value, on_input=slider_input)
          me.slider(on_value_change=slider, value=s.initial_slider_value)
        with me.box(): 
          pass

        #UPLOAD
        with me.box():
          me.uploader(
            label="Upload Image",
            accepted_file_types=["image/jpeg", "image/png"],
            on_upload=upload,
            type="flat",
            color="primary",
            style=me.Style(font_weight="bold"),
          )

          if s.file.size:
            me.text(f"File name: {s.file.name}")
            me.text(f"File size: {s.file.size}")
            me.text(f"File type: {s.file.mime_type}")

        with me.box():
          if s.file.size:
            me.image(src=_convert_contents_data_url(s.file))

        #AUTOCOMPLETE
        with me.box():
          me.autocomplete(
            label="Select region",
            options=_make_autocomplete_options(),
            on_selection_change=on_selection_change,
            on_enter=on_selection_change,
            on_input=on_input,
          )

        with me.box():
          me.text("Selected: " + s.selected_value)
        
        #ICON
        with me.box():
          me.text("home icon")
          me.icon(icon="home")

        #PROGESS BAR
        with me.box():
          me.text("Default progress bar")
          me.progress_bar()

          #SPINNER
          me.progress_spinner()

        #TABLE
        with me.box():
          me.table(
            df,
            on_click=table,
            header=me.TableHeader(sticky=True),
            columns={
              "NA": me.TableColumn(sticky=True),
              "Index": me.TableColumn(sticky=True),
            },
          )

        with me.box():
          me.text(s.selected_cell)

        #MARKDOWN
        with me.box():
          me.markdown(SAMPLE_MARKDOWN)


def call(event: me.ClickEvent):
  state = me.state(State)
  state.res=""
  yield
  for chunk in api():
    state.res += chunk
    yield

def api():
  # Replace this with an actual API call
  time.sleep(0.5)
  yield "\n\nExample "
  time.sleep(0.3)
  yield "of "
  time.sleep(1)
  yield "streaming "
  time.sleep(0.3)
  yield "an "
  time.sleep(0.5)
  yield "output."

def counter(event: me.ClickEvent):
  state = me.state(State)
  state.clicks += 1

def checkbox(event: me.CheckboxChangeEvent):
  state = me.state(State)
  state.checked = event.checked

def text(e: me.InputBlurEvent):
  state = me.state(State)
  state.text = e.value

def radio(event: me.RadioChangeEvent):
  s = me.state(State)
  s.radio_value = event.value

def select(e: me.SelectSelectionChangeEvent):
  s = me.state(State)
  s.selected_values = e.values

def toogle(event: me.SlideToggleChangeEvent):
  s = me.state(State)
  s.toggled = not s.toggled

def slider(event: me.SliderValueChangeEvent):
  state = me.state(State)
  state.slider_value = event.value
  state.initial_input_value = str(state.slider_value)

def slider_input(event: me.InputEvent):
  state = me.state(State)
  state.initial_slider_value = float(event.value)
  state.slider_value = state.initial_slider_value

def upload(event: me.UploadEvent):
  state = me.state(State)
  state.file = event.file

def _convert_contents_data_url(file: me.UploadedFile) -> str:
  return (
    f"data:{file.mime_type};base64,{base64.b64encode(file.getvalue()).decode()}"
  )

df = pd.DataFrame(
  data={
    "NA": [pd.NA, pd.NA, pd.NA],
    "Index": [3, 2, 1],
    "Bools": [True, False, np.bool_(True)],
    "Ints": [101, 90, np.int64(-55)],
    "Floats": [2.3, 4.5, np.float64(-3.000000003)],
    "Strings": ["Hello", "World", "!"],
    "Date Times": [
      pd.Timestamp("20180310"),
      pd.Timestamp("20230310"),
      datetime(2023, 1, 1, 12, 12, 1),
    ],
  }
)

def table(e: me.TableClickEvent):
  state = me.state(State)
  state.selected_cell = (
    f"Selected cell at col {e.col_index} and row {e.row_index} "
    f"with value {df.iat[e.row_index, e.col_index]!s}"
  )

SAMPLE_MARKDOWN = """
# Sample Markdown Document

## Table of Contents
1. [Headers](#headers)
2. [Emphasis](#emphasis)
3. [Lists](#lists)
4. [Links](#links)
5. [Code](#code)
6. [Blockquotes](#blockquotes)
7. [Tables](#tables)
8. [Horizontal Rules](#horizontal-rules)

## Headers
# Header 1
## Header 2
### Header 3
#### Header 4
##### Header 5
###### Header 6

## Emphasis
*Italic text* or _Italic text_

**Bold text** or __Bold text__

***Bold and Italic*** or ___Bold and Italic___

## Lists

### Unordered List
- Item 1
- Item 2
    - Subitem 2.1
    - Subitem 2.2

### Ordered List
1. First item
2. Second item
    1. Subitem 2.1
    2. Subitem 2.2

## Links
[GitHub](https://github.com/tomgorb)

## Code
Inline `code`

## Table

First Header  | Second Header
------------- | -------------
Content Cell { .foo }  | Content Cell { .foo }
Content Cell { .bar } | Content Cell { .bar }
"""

def on_selection_change(
  e: me.AutocompleteEnterEvent | me.AutocompleteSelectionChangeEvent,
):
  state = me.state(State)
  state.selected_value = e.value

def on_input(e: me.InputEvent):
  state = me.state(State)
  state.raw_value = e.value

def _make_autocomplete_options() -> list[me.AutocompleteOptionGroup]:
  """Creates and filter autocomplete options.
  The states list assumed to be alphabetized and we group by the first letter of the
  state's name.
  """
  states_options_list = []
  sub_group = None
  for state in _REGIONS:
    if not sub_group or sub_group.label != state[0]:
      if sub_group:
        states_options_list.append(sub_group)
      sub_group = me.AutocompleteOptionGroup(label=state[0], options=[])
    sub_group.options.append(me.AutocompleteOption(label=state, value=state))
  if sub_group:
    states_options_list.append(sub_group)
  return states_options_list

_REGIONS = [
  "Auvergne-Rhône-Alpes",
  "Bourgogne-Franche-Comté",
  "Brittany",
  "Centre-Val de Loire",
  "Corsica",
  "Grand Est",
  "Hauts-de-France",
  "Paris Region",
  "Normandie",
  "Nouvelle-Aquitaine",
  "Occitanie",
  "Pays de la Loire",
  "Provence Alpes Côte d’Azur",
  "Guadeloupe",
  "French Guiana",
  "Martinique",
  "Mayotte",
  "Réunion"
]
