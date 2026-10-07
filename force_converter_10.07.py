import math
import re
import tkinter as tk
from tkinter import ttk


NEWTONS_PER_UNIT = {
    "N": 1.0,
    "kN": 1000.0,
    "kg": 9.80665,
    "kgf": 9.80665,
    "ton": 9806.65,
}
UNIT_NAMES = {unit.lower(): unit for unit in NEWTONS_PER_UNIT}
INPUT_PATTERN = re.compile(
    r"^\s*([+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)\s*([A-Za-z]+)\s*$"
)
NUMBER_PATTERN = re.compile(
    r"^\s*[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?\s*$"
)
INITIAL_RESULT_TEXT = "숫자와 단위를 입력하고 변환 버튼을 클릭하세요."


def convert_force(
    force_value: float, input_unit: str
) -> list[tuple[str, float]]:
    """Convert a force value to every supported unit except its input unit."""
    force_n = force_value * NEWTONS_PER_UNIT[input_unit]
    if not math.isfinite(force_n):
        raise ValueError("입력값이 너무 커서 계산할 수 없습니다.")

    converted_values = []
    for output_unit, newtons_per_unit in NEWTONS_PER_UNIT.items():
        if output_unit != input_unit:
            converted_values.append(
                (output_unit, force_n / newtons_per_unit)
            )
    return converted_values


def convert_from_gui(
    value_entry: ttk.Entry,
    unit_combobox: ttk.Combobox,
    result_label: ttk.Label,
    history_listbox: tk.Listbox,
    record_history: bool = True,
) -> bool:
    """Validate GUI input, convert the force, and display the result."""
    user_input = value_entry.get().strip()
    input_match = INPUT_PATTERN.fullmatch(user_input)

    if input_match is not None:
        force_value = float(input_match.group(1))
        input_unit = UNIT_NAMES.get(input_match.group(2).lower())
        if input_unit is None:
            result_label.config(
                text=(
                    "오류: 지원하지 않는 단위입니다. "
                    "N, kN, kg, kgf, ton 중 하나를 사용하세요."
                ),
                foreground="#c62828",
            )
            return False
        unit_combobox.set(input_unit)
    elif NUMBER_PATTERN.fullmatch(user_input):
        force_value = float(user_input)
        input_unit = unit_combobox.get()
        history_value = f"{user_input} {input_unit}"
    else:
        result_label.config(
            text=(
                "오류: 숫자만 입력하거나 숫자와 단위를 함께 입력해 주세요. "
                "예: 1 또는 1kg"
            ),
            foreground="#c62828",
        )
        return False

    if input_match is not None:
        history_value = user_input

    if not math.isfinite(force_value):
        result_label.config(
            text="오류: 연산이 불가능하거나 너무 큰 값입니다.",
            foreground="#c62828",
        )
        return False

    converted_values = convert_force(force_value, input_unit)
    result_text = "\n".join(
        f"{value:.3f} {unit}" for unit, value in converted_values
    )
    result_label.config(text=result_text, foreground="#1b5e20")
    if record_history:
        history_listbox.insert(0, history_value)
        if history_listbox.size() > 10:
            history_listbox.delete(10, tk.END)
    return True


def copy_result_to_clipboard(
    root: tk.Tk, result_label: ttk.Label
) -> bool:
    """Copy the current conversion result to the clipboard."""
    result_text = result_label.cget("text")
    if (
        result_text == INITIAL_RESULT_TEXT
        or result_text.startswith("오류:")
        or not result_text.strip()
    ):
        result_label.config(
            text="오류: 복사할 변환 결과가 없습니다.",
            foreground="#c62828",
        )
        return False

    root.clipboard_clear()
    root.clipboard_append(result_text)
    root.update()
    return True


def reset_gui(
    value_entry: ttk.Entry,
    unit_combobox: ttk.Combobox,
    result_label: ttk.Label,
) -> None:
    """Reset the input, selected unit, and displayed result."""
    value_entry.delete(0, tk.END)
    unit_combobox.set("N")
    result_label.config(
        text=INITIAL_RESULT_TEXT,
        foreground="#000000",
    )
    value_entry.focus()


def create_gui() -> None:
    """Create and run the force converter GUI."""
    root = tk.Tk()
    root.title("공학용 힘 단위 변환기")
    root.resizable(False, False)

    main_frame = ttk.Frame(root, padding=20)
    main_frame.grid()

    ttk.Label(main_frame, text="힘의 크기").grid(
        row=0, column=0, padx=(0, 8), pady=5, sticky="w"
    )
    value_entry = ttk.Entry(main_frame, width=20)
    value_entry.grid(row=0, column=1, pady=5)
    value_entry.focus()

    ttk.Label(
        main_frame,
        text="숫자와 단위를 함께 입력하거나 숫자만 입력하세요.\n"
        "예: 1kg 또는 1 | 사용 가능 단위: N, kN, kg, kgf, ton",
        justify="left",
    ).grid(
        row=1, column=0, columnspan=2, pady=(0, 5), sticky="w"
    )
    unit_combobox = ttk.Combobox(
        main_frame,
        values=list(NEWTONS_PER_UNIT),
        state="readonly",
        width=17,
    )
    unit_combobox.set("N")
    unit_combobox.grid(row=2, column=0, columnspan=2, pady=5)

    result_label = ttk.Label(
        main_frame,
        text=INITIAL_RESULT_TEXT,
        justify="left",
        anchor="w",
        width=32,
    )
    result_label.grid(
        row=5, column=0, columnspan=2, pady=(15, 5), sticky="w"
    )

    ttk.Label(main_frame, text="최근 입력 기록 (최대 10개)").grid(
        row=6, column=0, columnspan=2, pady=(10, 3), sticky="w"
    )
    history_listbox = tk.Listbox(main_frame, width=32, height=5)
    history_listbox.grid(row=7, column=0, columnspan=2, pady=(0, 5))

    convert_button = ttk.Button(
        main_frame,
        text="변환",
        command=lambda: convert_from_gui(
            value_entry, unit_combobox, result_label, history_listbox
        ),
    )
    convert_button.grid(row=3, column=0, columnspan=2, pady=10)

    button_frame = ttk.Frame(main_frame)
    button_frame.grid(row=4, column=0, columnspan=2, pady=(0, 5))
    ttk.Button(
        button_frame,
        text="결과 복사",
        command=lambda: copy_result_to_clipboard(root, result_label),
    ).grid(row=0, column=0, padx=3)
    ttk.Button(
        button_frame,
        text="초기화",
        command=lambda: reset_gui(value_entry, unit_combobox, result_label),
    ).grid(row=0, column=1, padx=3)

    value_entry.bind(
        "<Return>",
        lambda _event: convert_from_gui(
            value_entry, unit_combobox, result_label, history_listbox
        ),
    )

    def use_history(_event: tk.Event) -> None:
        selection = history_listbox.curselection()
        if not selection:
            return
        value_entry.delete(0, tk.END)
        value_entry.insert(0, history_listbox.get(selection[0]))
        convert_from_gui(
            value_entry,
            unit_combobox,
            result_label,
            history_listbox,
            record_history=False,
        )

    history_listbox.bind("<ButtonRelease-1>", use_history)
    root.mainloop()


if __name__ == "__main__":
    create_gui()
