import dash_core_components as dcc
import dash_html_components as html


# SOURCE: https://github.com/plotly/dash-sample-apps/blob/43d705838bd6f2eeebcee109f185f818acc696cb/apps/dash-tsne/demo.py#L60

# These are the some reusable components we used in the project.
def NamedSlider(name, short, min, max, step, val, marks=None):
    if marks:
        step = None
    else:
        marks = {i: i for i in range(min, max + 1, step)}

    return html.Div(
        style={"margin": "25px 5px 30px 0px"},
        children=[
            f"{name}:",
            html.Div(
                style={"margin-left": "5px"},
                children=[
                    dcc.Slider(
                        id=short,
                        min=min,
                        max=max,
                        marks=marks,
                        step=step,
                        value=val,
                    )
                ],
            ),
        ],
    )
