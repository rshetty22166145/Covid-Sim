from guizero import *
from tkinter import filedialog, simpledialog
from os.path import exists
from pydoc import locate
import csv
import math
import pickle
from typing import Callable, Union
from sync_app import SyncApp

FILE2_SUPPORT = False
global gapp

class InvalidColumnsError(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        self.self_msg = self.msg
        return self.self_msg


def build_app(
        simulation_parameters,
        simulation_launch_cbfunc: Callable,
        validate_csv_file_func: Callable,
        launch_csv_comparison_cbfunc: Callable
) -> App:
    """Construct the GUI and return it"""
    app = App(title="COVID Simulation Launcher", width=800)

    def m_left_pane() -> Box:
        """Construct and return leftside button bar"""
        left_pane = Box(app, layout="auto", align="left", width=150, height="fill", border=2)

        Box(left_pane, width="fill", height=80)
        PushButton(left_pane, text="Simulation Launcher", padx=10, pady=15, width="fill", command=lambda: show_pane(1))
        PushButton(left_pane, text="Compare Data", padx=10, pady=15, width="fill", command=lambda: show_pane(2))
        PushButton(left_pane, text="Quit", padx=10, pady=15, width="fill", command=lambda: exit(0))
        Box(left_pane, width="fill", height="fill")

        return left_pane

    def m_logo_pane() -> Box:
        """Construct intro logo page and returns it"""
        logo_pane = Box(app, layout="auto", align="right", width="fill", height="fill", border=2)

        Box(logo_pane, width="fill", height="fill")
        Picture(logo_pane, image="logo.png")
        Text(logo_pane, text="COVID Simulator v. 1.0", font="Helvetica")
        Box(logo_pane, width="fill", height="fill")

        return logo_pane

    def m_file_comparison_pane() -> Box:
        """Construct the file chooser pane for csv data comparisons"""

        def _m_get_csv_vals(file: str, col: str) -> list[str]:
            """Get column values in a list from a csv file"""
            ret = []
            with open(file, newline='') as fcsv:
                for kval in csv.DictReader(fcsv):
                    if kval[col] is not None:
                        ret.append(kval[col])

            return ret

        def _m_set_error(message: str) -> None:
            """Sets error message"""
            txt_err.value = message

        def _m_check_valid() -> bool:
            """"""
            (f1, f2, is_valid) = (file1.value, file2.value if file2 is not None else "", True)

            def __m_pop_cols(cmb_ptrs: list[Combo], file: str) -> None:
                """Populate the combo dropdown menu with csv column names"""
                with open(file, newline='') as fcsv:
                    for hcsv in csv.reader(fcsv):
                        [x.clear() for x in cmb_ptrs]
                        idx = 0
                        for hdr in hcsv:
                            [x.insert(idx, hdr) for x in cmb_ptrs]
                            idx += 1
                        break

            _m_set_error("")

            # Validates file paths in input boxes using supplied validation func
            if f1 == "":
                file1.bg = "white"
                is_valid = False

                b3_1.hide()
            elif validate_csv_file_func(f1):
                file1.bg = "SeaGreen1"
                __m_pop_cols([cols1, cols1_1], f1)

                b3_1.show()
            else:
                file1.bg = "light salmon"
                is_valid = False

                b3_1.hide()

            if FILE2_SUPPORT:
                if f2 == "":
                    file2.bg = "white"
                    # is_valid = False

                    b3_2.hide()
                elif validate_csv_file_func(f2):
                    file2.bg = "SeaGreen1"
                    __m_pop_cols([cols2, cols2_1], f2)

                    b3_2.show()
                else:
                    file2.bg = "light salmon"
                    is_valid = False

                    b3_2.hide()
            else:
                b3_2.hide()

            # Toggles comparison button and column choosers based on validation
            if is_valid:
                cmp_btn.enable()
                # b3.show()
            else:
                cmp_btn.disable()
                # b3.hide()

            return is_valid

        def _m_setvalue(ptr: TextBox, val: str) -> None:
            """Populate the file path textbox with val, used when browsing for files"""
            ptr.value = val
            _m_check_valid()

        file_comparison_pane = Box(app, width="fill", height="fill")
        Box(file_comparison_pane, width="fill", height="fill")

        b1 = Box(file_comparison_pane, width="fill")
        Box(b1, width="fill", align="left")
        Text(b1, text="File 1: " if FILE2_SUPPORT else "File: ", align="left")
        file1 = TextBox(b1, width=40, align="left", command=_m_check_valid)
        Box(b1, width=10, align="left")
        PushButton(b1, text="B", align="left", image="browse.png",
                   command=lambda: _m_setvalue(file1, (filedialog.askopenfilename(filetypes=[("CSV Files", ".csv")]))))
        Box(b1, width="fill", align="left")

        b2 = Box(file_comparison_pane, width="fill")
        Box(b2, width="fill", align="left")

        Text(b2, text="File 2: ", align="left", visible=FILE2_SUPPORT)
        file2 = TextBox(b2, width=40, align="left", command=_m_check_valid, visible=FILE2_SUPPORT)
        Box(b2, width=10, align="left", visible=FILE2_SUPPORT)
        PushButton(b2, text="B", align="left", image="browse.png",
                   command=lambda: _m_setvalue(file2, (filedialog.askopenfilename(filetypes=[("CSV Files", ".csv")]))),
                   visible=FILE2_SUPPORT)
        Box(b2, width="fill", align="left", visible=FILE2_SUPPORT)

        b3 = Box(file_comparison_pane, width="fill", height=150)

        b3_1 = Box(b3, width="fill", height=150, align="left", visible=False)
        Text(b3_1, "File 1" if FILE2_SUPPORT else "File", font="Helvetica 18 underline")
        b3_1_1 = Box(b3_1, width="fill")
        Text(b3_1_1, "Caption Column: ", align="left")
        cols1 = Combo(b3_1_1, align="left")
        b3_1_2 = Box(b3_1, width="fill")
        Text(b3_1_2, "Values Column: ", align="left")
        cols1_1 = Combo(b3_1_2, align="left")

        Box(b3, width=10, align="left")

        b3_2 = Box(b3, width="fill", height=150, align="left", visible=False)
        Text(b3_2, "File 2", font="Helvetica 18 underline")
        b3_2_1 = Box(b3_2, width="fill")
        Text(b3_2_1, "Caption Column: ", align="left")
        cols2 = Combo(b3_2_1, align="left")
        b3_2_2 = Box(b3_2, width="fill")
        Text(b3_2_2, "Values Column: ", align="left")
        cols2_1 = Combo(b3_2_2, align="left")

        # b3_2 = Box(b3, width="fill", height=150, align="left")
        # Text(b3_2, "File 2", font="Helvetica 18 underline")
        # Text(b3_2, "Legend Column: ")
        # cols2 = Combo(b3_2, align="left")
        # Text(b3_2, "Caption Column: ")
        # cols2_1 = Combo(b3_2, align="left")

        # Text(b3, "File 2 Column: ", align="left")
        # cols2 = Combo(b3, align="left")
        # Box(b3, width="fill", align="left")

        b_err = Box(file_comparison_pane, width="fill", height=50)
        Box(b_err, width="fill", height=10)
        txt_err = Text(b_err, text="", color="red")

        def _m_launch_comprison():
            try:
                launch_csv_comparison_cbfunc(_m_get_csv_vals(file1.value, cols1.value),
                                             _m_get_csv_vals(file1.value, cols1_1.value),
                                             None if not FILE2_SUPPORT or file2.value == "" else _m_get_csv_vals(
                                                 file2.value, cols2.value),
                                             None if not FILE2_SUPPORT or file2.value == "" else _m_get_csv_vals(
                                                 file2.value, cols2_1.value))
            except InvalidColumnsError as e:
                _m_set_error(e.msg)

        b4 = Box(file_comparison_pane, width="fill")
        cmp_btn = PushButton(b4, text="Run Comparison", enabled=False, command=_m_launch_comprison)

        Box(file_comparison_pane, width="fill", height="fill")

        return file_comparison_pane

    def m_sim_launch_pane() -> Box:
        """Get the pane for specifying sim parameters and launching sim"""

        # Constants hangout corner
        IDX_WIDGET_BOX = 0
        IDX_WIDGET_CONTROL = 1
        IDX_WIDGET_OPTION = 2

        IDX_OPTION_LABEL = 0
        IDX_OPTION_PROPERTY = 1
        IDX_OPTION_TYPE = 2
        IDX_OPTION_DEFAULT_VALUE = 3
        IDX_OPTION_VALIDATOR_LAMBDA = 4

        # The pain itself
        sim_launch_pane = Box(app, layout="auto", align="right", width="fill", height="fill", border=2)

        # Saved sim parameter presets
        savedmodels = {
            "(new)": {}
        }
        selectedmodel = "(new)"

        def _load_savedmodels(obj: dict) -> None:
            """Load in save models from pickled save file"""
            nonlocal savedmodels

            if exists("savedmodels.dat"):
                with open("savedmodels.dat", "rb") as file:
                    savedmodels = pickle.load(file)
            else:
                with open("savedmodels.dat", "wb") as file:
                    pickle.dump(obj, file)

        def _save_model() -> None:
            """Pickle em back"""
            nonlocal selectedmodel, savedmodels

            if selectedmodel == "(new)":
                answer = simpledialog.askstring("Input", "What do you wish to call this "
                                                         "model? (any existing ones under "
                                                         "that name will be overwritten)", parent=app.tk)

                if answer is not None:
                    savedmodels[answer] = valdict
                    with open("savedmodels.dat", "wb") as file:
                        pickle.dump(savedmodels, file)
                    selectedmodel = answer
                    cmb_save_models.append(answer)
                    cmb_save_models.value = answer
            else:
                savedmodels[selectedmodel] = valdict
                with open("savedmodels.dat", "wb") as file:
                    pickle.dump(savedmodels, file)

            _load_savedmodels(savedmodels)

        def _load_model(model_name: str) -> None:
            """Populates all the fields in the model from the specified model"""
            nonlocal savedmodels, selectedmodel

            selectedmodel = model_name

            _m_populate_model(simulation_parameters, savedmodels[model_name])
            _u_set_values()

        # Load the presets
        _load_savedmodels(savedmodels)

        # Save bar container
        save_bar = Box(sim_launch_pane, width="fill")
        Text(save_bar, text="Saved Models: ", align="left")
        Box(save_bar, width=10, align="left")
        cmb_save_models = Combo(save_bar, options=savedmodels.keys(), align="left", command=lambda id: _load_model(id))
        cmb_save_models.value = selectedmodel
        # if len(savedmodels) < 1:
        #     cmb_save_models.disable()
        Box(save_bar, width=40, align="left")
        PushButton(save_bar, text="Save", align="left", command=_save_model)

        # Double column input fields
        x_widget_bar = Box(sim_launch_pane, width="fill", height="fill")
        wbar1 = Box(x_widget_bar, width="fill", height="fill", align="left", border=1)
        wbar2 = Box(x_widget_bar, width="fill", height="fill", align="left", border=1)

        cmd_bar = Box(sim_launch_pane, width="fill")

        valdict = {}
        widgets = {}

        def __validate_field(field, func, field_type: type) -> bool:
            """Return whether the value in the field is valid based on custom validation function"""
            try:
                if field_type is bool:
                    actual_value = field.value
                else:
                    actual_value = field_type(field.value)
            except:
                field.bg = "light salmon"
                return False

            if func(actual_value):
                field.bg = "SeaGreen1"
                return True
            else:
                field.bg = "light salmon"
                return False

        # def __assign_val(field, func, key, field_type):
        #     if(__validate_field(field, func, field_type)):
        #         valdict[key] = field.value

        def _assign_all() -> None:
            """Update valdict with new values"""
            for key, widget in widgets.items():
                if (__validate_field(widget[IDX_WIDGET_CONTROL],
                                     (widget[IDX_WIDGET_OPTION])[IDX_OPTION_VALIDATOR_LAMBDA],
                                     (widget[IDX_WIDGET_OPTION])[IDX_OPTION_TYPE])):

                    if (widget[IDX_WIDGET_OPTION])[IDX_OPTION_TYPE] is bool:
                        actual_value = widget[IDX_WIDGET_CONTROL].value
                    else:
                        actual_value = ((widget[IDX_WIDGET_OPTION])[IDX_OPTION_TYPE])(widget[IDX_WIDGET_CONTROL].value)

                    valdict[key] = actual_value #widget[IDX_WIDGET_CONTROL].value

        def _validate_all_fields() -> list[bool]:
            """Return validation results for each field"""
            results = []
            for widget in widgets.values():
                results.append(__validate_field(widget[IDX_WIDGET_CONTROL],
                                                (widget[IDX_WIDGET_OPTION])[IDX_OPTION_VALIDATOR_LAMBDA],
                                                (widget[IDX_WIDGET_OPTION])[IDX_OPTION_TYPE]))

            return results

        def _m_populate_model(options: list, values: dict) -> None:
            """Populate valdict initially, which contains a dictionary of all
            the input field key values"""
            valdict.clear()

            for opt in options:
                valdict[opt[IDX_OPTION_PROPERTY]] = values[opt[IDX_OPTION_PROPERTY]] if \
                    opt[IDX_OPTION_PROPERTY] in values else opt[IDX_OPTION_DEFAULT_VALUE]

        def _u_create_widgets(options: list, pane1: Box, pane2: Box) -> None:
            """Create input field widgets in 2 column panes"""
            # Splits into 2 columns
            (idx, cutoff) = (0, math.ceil(len(options) / 2))

            for opt in options:
                b = Box(pane1 if idx < cutoff else pane2)

                # captured_lambda =

                if opt[IDX_OPTION_TYPE] is bool:
                    cb = CheckBox(b, text=opt[IDX_OPTION_LABEL])  # , command = )
                else:
                    Text(b, text=opt[IDX_OPTION_LABEL] + ": ", align="left")
                    cb = TextBox(b, align="left")  # , command = )

                # cb.update_command(lambda x: __assign_val(cb, opt[IDX_OPTION_VALIDATOR_LAMBDA],
                # opt[IDX_OPTION_PROPERTY], opt[IDX_OPTION_TYPE]))

                # Updates all values on any changes to any widget
                cb.update_command(_assign_all)

                widgets[opt[IDX_OPTION_PROPERTY]] = (b, cb, opt)
                idx = idx + 1

        def _u_set_values():
            """Set initial values into widgets, also when loading a preset"""
            for key, widget in widgets.items():
                widget[IDX_WIDGET_CONTROL].bg = "white"
                widget[IDX_WIDGET_CONTROL].value = valdict[key]

        def _go():
            global gapp
            """If all is well, then proceed to PHASE 2 of the master evil plan"""
            if all(_validate_all_fields()):
                gapp.destroy()
                simulation_launch_cbfunc(valdict)

        # Populate fields initially
        _m_populate_model(simulation_parameters, {})
        # Maps field names to widgets in the GUI and creates the widgets
        _u_create_widgets(simulation_parameters, wbar1, wbar2)
        _u_set_values()

        PushButton(cmd_bar, text="Launch!", command=_go)

        return sim_launch_pane

    def hide_all():
        """Quick! Under the table!"""
        logo_pane.hide()
        sim_launch_pane.hide()
        file_comparison_pane.hide()

    def show_pane(idx: int) -> None:
        """Show specific pane and hide the others"""
        hide_all()
        if idx == 0:
            logo_pane.show()
        elif idx == 1:
            sim_launch_pane.show()
        elif idx == 2:
            file_comparison_pane.show()

    # Creates all them panes
    left_pane = m_left_pane()
    sim_launch_pane = m_sim_launch_pane()
    logo_pane = m_logo_pane()
    file_comparison_pane = m_file_comparison_pane()

    # Shows logo pane
    show_pane(0)

    return app


def start_gui(data_comparison_callback: Callable, sim_display_callback: Callable) -> None:
    simvars = [("City Blocks X", "city_blocks_x", int, 5, lambda val: val is not None and val >= 5),
               ("City Blocks Y", "city_blocks_y", int, 5, lambda val: val is not None and val >= 5),
               ("Block Dim (DU)", "block_dim", float, 0, lambda val: val is not None),
               ("Buildings", "buildings_constant", int, 0, lambda val: val is not None),
               ("Road Width", "road_width", float, 0, lambda val: val is not None),
               ("Highrise %", "high_rise_percentage", float, 0, lambda val: val is not None),
               ("# Medical Buildings", "num_medical_buildings", int, 0, lambda val: val is not None),
               ("# Travel Buildings", "num_travel_buildings", int, 0, lambda val: val is not None),
               ("Residential Ratio", "residential_ratio", int, 0, lambda val: val is not None),
               ("Commercial Ratio", "commercial_ratio", int, 0, lambda val: val is not None),
               ("Industrial Ration", "industrial_ratio", int, 10, lambda val: val is not None),
               ("Population", "population", int, 0, lambda val: val is not None),
               ("Avg. Age", "avg_age", int, 0, lambda val: val is not None),
               ("% Mask Wearing Tendency", "mask_wearing_percentage", int, 0, lambda val: val is not None),
               ("Avg. Travels / Year", "average_travels_per_year", int, 0, lambda val: val is not None),
               ("Borders Closed?", "is_closed_border", bool, True, lambda val: val is not None),
               ("Initial Vaccinated %", "initial_vaccination_percentage", float, 0, lambda val: val is not None),
               ("Initial Infection %", "initial_infection_percentage", float, 0, lambda val: val is not None),
               ("Vaccine Available?", "is_vaccine_available", bool, False, lambda val: val is not None),
               ("Homelessness %", "homelessness_percentage", float, 0, lambda val: val is not None),
               ("Quarantine Tendency", "quarantine_tendency", float, 0, lambda val: val is not None),
               ("Vaccination Tendency", "vaccination_tendency", float, 0, lambda val: val is not None),
               ("Social Distancing", "social_distancing", float, 0, lambda val: val is not None),
               ("World Thread Level: Local", "world_threat_level_local", float, 0, lambda val: val is not None),
               ("World Thread Level: Int'l", "world_threat_level_international", float, 0, lambda val: val is not None)]

    global gapp
    gapp = build_app(
        simulation_parameters=simvars,
        simulation_launch_cbfunc=sim_display_callback,
        validate_csv_file_func=lambda file: str is not None and exists(file) and str(file).lower().endswith("csv"),
        launch_csv_comparison_cbfunc=data_comparison_callback
    )

    gapp.display()



def csv_callback(keys1, vals1, keys2, vals2):
    """Called by GUI to output graph comparison visual"""
    #raise InvalidColumnsError("Sample error message!")
    print("KEYS 1: ", keys1, "\r\nVALUES 1: ", vals1, "\r\n", "KEYS 2: ", keys2, "\r\nVALUES 2: ", vals2, "\r\n")


def simulation_callback(params: dict) -> None:
    """Called by GUI to launch simulation"""
    # Create App
    #app = SyncApp(params)

    # Start app
    #app.start()


#start_gui(csv_callback, simulation_callback)
