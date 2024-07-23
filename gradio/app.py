import sys
import logging
import pandas as pd
import gradio as gr
import plotly.graph_objects as go

logger = logging.getLogger(__name__)

def get_inputs():
    input_file = gr.File(
        label="Input file (geo.csv)")
    zoom = gr.Slider(value=4, minimum=0, maximum=9, step=1, label="Zoom value")
    inputs = [
              input_file,
              zoom
              ]
    return inputs

def filter_map(zoom, input_file):

    try: 

        df = pd.read_csv(input_file, header=0, sep="|")
        df.fillna("N/A", inplace=True)
        names = df['city'].values.tolist()
        values = df['email'].values.tolist()
        # df[['lat', 'lng']] = df['latlng'].str.split(",", expand=True)
        text_list = [(names[i], values[i]) for i in range(0, len(names))]
        fig = go.Figure(go.Scattermapbox(
                customdata=text_list,
                lat=df['lat'].values.tolist(),
                lon=df['lng'].values.tolist(),
                mode='markers',
                marker=go.scattermapbox.Marker(
                    size=6
                ),
                hoverinfo="text",
                hovertemplate='<b>City</b>: %{customdata[0]}<br><b>Email</b>: %{customdata[1]}'
            ))

        fig.update_layout(
            mapbox_style="open-street-map",
            hovermode='closest',
            mapbox=dict(
                bearing=0,
                center=go.layout.mapbox.Center( # PARIS
                    lat=48.87,
                    lon=2.33
                ),
                pitch=0,
                zoom=zoom
            ),
        )

        return fig
    except:
        raise gr.Error("Please provide a data file.")
    
def call(input_file,
         zoom):

    msg = f""" Application parameters are: 
                --input_file: {input_file}
                --zoom: {zoom}
                """
    
    return msg, filter_map(zoom, input_file)

def get_demo():
    html = """
    <center> 
    <h1> Gradio Blocks </h1>
    </center>
    """
    with gr.Blocks() as demo:
        gr.HTML(html)
        with gr.Row():
            with gr.Column(scale=1):
                input_file = gr.File()
                btn = gr.Button(value="Load Map")
            with gr.Column(scale=4):
                map = gr.Plot()
        with gr.Row():
            with gr.Column(scale=1):
                pass
            with gr.Column(scale=4):
                zoom = gr.Slider(value=4, minimum=0, maximum=9, step=1, label="🔎")
                btn.click(filter_map, [zoom, input_file], map)
                zoom.change(filter_map, [zoom, input_file], map)
    return demo

def success():
    return True
def failure():
    raise gr.Error("This should fail!")
def warning_fn():
    gr.Warning("This is a warning!")
def info_fn():
    gr.Info("This is some info")

def message(number, radio, checkboxgroup, dropdown):
    msg = f""" 
              number: {number}
              radio: {radio}
              checkboxgroup: {checkboxgroup}
              dropdown: {dropdown}
            """
    return msg

def change(inputs, out):
    for inp in inputs:
        inp.change(message, inputs, out)

def get_cheatsheet():

    with gr.Blocks() as cheatsheet:
        with gr.Row():

            with gr.Column(scale=4): 
                number = gr.Number(value=0,
                                minimum=0,
                                maximum=9,
                                step=1,
                                label="Choose your number")

                radio = gr.Radio(
                    choices=["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"],
                    label="Choose your number", info="a simple radio button" 
                )

                checkboxgroup = gr.CheckboxGroup(
                    choices=["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"],
                    label="Choose your numbers", info="a multi-select choice field"
                )

                dropdown = gr.Dropdown(
                        ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"], value=["6", "7"], 
                        label="Choose your numbers", info="a drop-down list",
                        interactive=True, multiselect=True
                    )

            with gr.Column(scale=1): 
                some_text = gr.Textbox(
                    label="Some text")

                success_btn = gr.Button(value="Trigger Success")
                success_btn.click(success, None, None).success(lambda: "Success 🎉", inputs=None, outputs=some_text)

                failure_btn = gr.Button(value="Trigger Failure")
                failure_btn.click(failure, None, None)

                trigger_warning = gr.Button(value="Trigger Warning")
                trigger_warning.click(warning_fn, None, None)

                trigger_info = gr.Button(value="Trigger Info")
                trigger_info.click(info_fn, None, None)

        with gr.Row():
            out = gr.Textbox(label="Parameters", show_copy_button=True)
            inputs = [number, radio, checkboxgroup, dropdown]
            change(inputs, out)

    return cheatsheet


if __name__ == '__main__':

    inputs = get_inputs()
    gradio_app = gr.Interface(fn=call,
                              inputs=inputs,
                              outputs=[gr.Textbox(label="Parameters transmitted"),
                                       gr.Plot(label="Map")],
                              title="Gradio Interface",
                              allow_flagging="never")

    final = gr.TabbedInterface([gradio_app, get_demo(), get_cheatsheet()],["Interface","Blocks","Cheat sheet"])
    try:
        final.launch()
        final.close()
    except [TypeError, ValueError]:
        sys.exit(1)
