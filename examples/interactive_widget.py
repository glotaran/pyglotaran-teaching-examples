from __future__ import annotations  # noqa: INP001

import ipywidgets as widgets
from IPython.display import clear_output
from IPython.display import display
from pydantic import BaseModel
from pydantic import Field
from pydantic import ValidationError


class SimulationParameters(BaseModel):
    decay_rates: list[float] = Field(..., description="Decay rates as a list of floats")
    amplitudes: list[float] = Field(..., description="Amplitudes as a list of floats")
    location_mean: list[float] = Field(
        ..., description="Location (mean) of spectra (cm-1) as a list of floats"
    )
    width: list[float] = Field(..., description="Width of spectra (cm-1) as a list of floats")
    skewness: list[float] = Field(
        ..., description="Skewness of spectra (cm-1) as a list of floats"
    )
    timepoints: dict = Field(..., description="Timepoints with max and stepsize as floats")
    wavelength: dict = Field(
        ..., description="Wavelength (nm) with min, max, and stepsize as floats"
    )
    stdev_noise: float = Field(..., description="Standard deviation of noise as a float")
    seed: int = Field(..., description="Seed as an integer")
    add_gaussian_irf: bool = Field(..., description="Boolean to add Gaussian IRF")
    irf_location: float = Field(..., description="IRF location as a float")
    irf_width: float = Field(..., description="IRF width as a float")
    use_sequential_scheme: bool = Field(..., description="Boolean to use sequential scheme")


class SimulateWidget:
    def __init__(self):
        # Define the input fields with layout adjustments
        text_style = {"description_width": "initial"}
        item_layout = widgets.Layout(width="50%")

        self.decay_rates_input = widgets.Text(
            value="",
            placeholder="Enter decay rates as comma-separated floats",
            description="Decay rates:",
            layout=item_layout,
            style=text_style,
        )

        self.amplitudes_input = widgets.Text(
            value="",
            placeholder="Enter amplitudes as comma-separated floats",
            description="Amplitudes:",
            layout=item_layout,
            style=text_style,
        )

        self.location_input = widgets.Text(
            value="",
            placeholder="Enter location of spectra (cm-1) as comma-separated floats",
            description="Location:",
            layout=item_layout,
            style=text_style,
        )

        self.width_input = widgets.Text(
            value="",
            placeholder="Enter width of spectra (cm-1) as comma-separated floats",
            description="Width:",
            layout=item_layout,
            style=text_style,
        )

        self.skewness_input = widgets.Text(
            value="",
            placeholder="Enter skewness of spectra (cm-1) as comma-separated floats",
            description="Skewness:",
            layout=item_layout,
            style=text_style,
        )

        self.max_timepoint_input = widgets.FloatText(
            value=0.0, description="Max Timepoint:", layout=item_layout, style=text_style
        )

        self.stepsize_timepoint_input = widgets.FloatText(
            value=0.0, description="Stepsize Timepoint:", layout=item_layout, style=text_style
        )

        self.min_wavelength_input = widgets.FloatText(
            value=0.0, description="Min Wavelength (nm):", layout=item_layout, style=text_style
        )

        self.max_wavelength_input = widgets.FloatText(
            value=0.0, description="Max Wavelength (nm):", layout=item_layout, style=text_style
        )

        self.stepsize_wavelength_input = widgets.FloatText(
            value=0.0,
            description="Stepsize Wavelength (nm):",
            layout=item_layout,
            style=text_style,
        )

        self.stdev_noise_input = widgets.FloatText(
            value=0.0, description="Stdev Noise:", layout=item_layout, style=text_style
        )

        self.seed_input = widgets.IntText(
            value=0, description="Seed:", layout=item_layout, style=text_style
        )

        self.add_gaussian_irf_input = widgets.Checkbox(
            value=False, description="Add Gaussian IRF", layout=item_layout
        )

        self.irf_location_input = widgets.FloatText(
            value=0.0, description="IRF Location:", layout=item_layout, style=text_style
        )

        self.irf_width_input = widgets.FloatText(
            value=0.0, description="IRF Width:", layout=item_layout, style=text_style
        )

        self.use_sequential_scheme_input = widgets.Checkbox(
            value=False, description="Use Sequential Scheme", layout=item_layout
        )

        # Button to generate the output dictionary
        self.generate_button = widgets.Button(
            description="Simulate",
            disabled=False,
            button_style="success",  # 'success', 'info', 'warning', 'danger' or ''
            tooltip="Click to simulate",
            icon="check",  # (FontAwesome names without the `fa-` prefix)
        )

        # Output area to display the results
        self.output = widgets.Output()

        self.result: SimulationParameters | None = None

        # Attach the click event to the button
        self.generate_button.on_click(self.on_button_click)

        # Organize the input fields into a grid
        self.grid = widgets.GridBox(
            children=[
                self.decay_rates_input,
                self.amplitudes_input,
                self.location_input,
                self.width_input,
                self.skewness_input,
                self.max_timepoint_input,
                self.stepsize_timepoint_input,
                self.min_wavelength_input,
                self.max_wavelength_input,
                self.stepsize_wavelength_input,
                self.stdev_noise_input,
                self.seed_input,
                self.add_gaussian_irf_input,
                self.irf_location_input,
                self.irf_width_input,
                self.use_sequential_scheme_input,
            ],
            layout=widgets.Layout(
                width="100%", grid_template_columns="50% 50%", grid_gap="10px 10px"
            ),
        )

    def validate_input(self, input_value: str, description: str) -> bool:
        if not input_value:
            print(f"Please fill in the mandatory field: {description}")
            return False
        try:
            list(map(float, input_value.split(",")))
            return True
        except ValueError:
            print(f"Invalid input in field: {description}. Please enter comma-separated floats.")
            return False

    def on_button_click(self, b):  # noqa: ARG002
        """
        Event handler for button click.

        Parameters:
            b: Button
                The button object that triggered the event.

        Returns:
            None
        """

        with self.output:
            clear_output()
            fields_to_validate = [
                (self.decay_rates_input.value, "Decay rates"),
                (self.amplitudes_input.value, "Amplitudes"),
                (self.location_input.value, "Location (mean) of spectra (cm-1)"),
                (self.width_input.value, "Width of spectra (cm-1)"),
                (self.skewness_input.value, "Skewness of spectra (cm-1)"),
            ]

            if not all(
                self.validate_input(value, description)
                for value, description in fields_to_validate
            ):
                return

            try:
                self.result = SimulationParameters(
                    decay_rates=list(map(float, self.decay_rates_input.value.split(","))),
                    amplitudes=list(map(float, self.amplitudes_input.value.split(","))),
                    location_mean=list(map(float, self.location_input.value.split(","))),
                    width=list(map(float, self.width_input.value.split(","))),
                    skewness=list(map(float, self.skewness_input.value.split(","))),
                    timepoints={
                        "max": self.max_timepoint_input.value,
                        "stepsize": self.stepsize_timepoint_input.value,
                    },
                    wavelength={
                        "min": self.min_wavelength_input.value,
                        "max": self.max_wavelength_input.value,
                        "stepsize": self.stepsize_wavelength_input.value,
                    },
                    stdev_noise=self.stdev_noise_input.value,
                    seed=self.seed_input.value,
                    add_gaussian_irf=self.add_gaussian_irf_input.value,
                    irf_location=self.irf_location_input.value,
                    irf_width=self.irf_width_input.value,
                    use_sequential_scheme=self.use_sequential_scheme_input.value,
                )
                print(self.result)
            except ValidationError as e:
                print(f"Input validation error: {e}")

    def display(self):
        display(self.grid, self.generate_button, self.output)

    def get_result(self):
        return self.result
