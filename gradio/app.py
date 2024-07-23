import sys
import logging
import pandas as pd
import gradio as gr
import plotly.graph_objects as go

logger = logging.getLogger(__name__)

def get_inputs():
    number = gr.Number(value=0,
                       minimum=0,
                       maximum=9,
                       step=1,
                       label="Choose your number")

    radio = gr.Radio(
        choices=["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"],
        label="Choose your number")

    checkboxgroup = gr.CheckboxGroup(
        choices=["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"],
        label="Choose your numbers")

    input_file = gr.File(
        label="Input file (geo.csv)")

    some_text = gr.Textbox(
        label="Some text")

    zoom = gr.Slider(value=4, minimum=0, maximum=9, step=1, label="Zoom value")

    inputs = [
              number,
              radio,
              checkboxgroup,
              input_file,
              some_text,
              zoom
              ]

    return inputs


def filter_map(zoom, input_file):

    try: 

        df = pd.read_csv(input_file, header=0, sep="|")
        names = df['city'].values.tolist()
        values = df['email'].values.tolist()
        # df[['lat', 'lng']] = df['latlng'].str.split(",", expand=True)
        text_list = [(names[i], (values[i] if values[i] else "N/A")) for i in range(0, len(names))]
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
    
def call(number,
         radio,
         checkboxgroup,
         input_file,
         some_text,
         zoom):

    msg = f""" Application parameters are: 
                --number: {number}
                --radio: {radio}
                --checkboxgroup: {checkboxgroup}
                --input_file: {input_file}
                --some_text: {some_text}
                --zoom: {zoom}
                """
    
    return msg, filter_map(zoom, input_file)

html = """
<center> 
<h1> Gradio Blocks </h1>
</center>
"""

if __name__ == '__main__':

    inputs = get_inputs()
    gradio_app = gr.Interface(fn=call,
                              inputs=inputs,
                              outputs=[gr.Textbox(label="Parameters transmitted"),
                                       gr.Plot(label="Map")],
                              title="Gradio Interface",
                              allow_flagging="never")

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

    final = gr.TabbedInterface([demo, gradio_app],["Blocks","Interface"])
    try:
        final.launch()
        final.close()
    except [TypeError, ValueError]:
        sys.exit(1)
