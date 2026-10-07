from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt


REQUIRED_COLUMNS = {"time_s", "force_N"}
DATA_FILE_NAMES = ("load_data.csv",)
RESULT_FILE_NAME = "load_result.csv"
PLOT_FILE_NAME = "stress_plot.png"
AREA_MM2 = 100
REFERENCE_STRESS_MPA = 6


def find_data_file() -> Path:
    """Return the first supported load-data file found next to this script."""
    for file_name in DATA_FILE_NAMES:
        data_file = Path(__file__).with_name(file_name)
        if data_file.is_file():
            return data_file

    searched_files = ", ".join(DATA_FILE_NAMES)
    raise FileNotFoundError(f"데이터 파일을 찾을 수 없습니다. 검색한 파일: {searched_files}")


def analyze_load_data(data_file: Path) -> tuple[int, int, float, float, float, float]:
    """Read load data, save stress results, and return analysis values."""
    data = pd.read_csv(data_file)

    missing_columns = REQUIRED_COLUMNS - set(data.columns)
    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(f"필수 열이 없습니다: {missing}")

    numeric_data = data[["time_s", "force_N"]].apply(pd.to_numeric, errors="coerce")
    invalid_rows = numeric_data.isna().any(axis=1)
    if invalid_rows.any():
        print("제외한 행:")
        for row_index in data.index[invalid_rows]:
            row_number = row_index + 2
            for column in ("time_s", "force_N"):
                value = data.loc[row_index, column]
                if pd.isna(value):
                    value = "빈칸"
                elif not pd.notna(numeric_data.loc[row_index, column]):
                    value = str(value)
                else:
                    continue
                print(f"  원본 CSV {row_number}행, {column}: {value}")

    valid_data = numeric_data.loc[~invalid_rows]
    if valid_data.empty:
        raise ValueError("유효한 데이터가 없어 계산을 중단합니다.")

    result_data = data.loc[~invalid_rows].copy()
    result_data[["time_s", "force_N"]] = valid_data
    result_data["stress_MPa"] = valid_data["force_N"] / AREA_MM2
    result_file = data_file.with_name(RESULT_FILE_NAME)
    result_data.to_csv(result_file, index=False)

    maximum_stress_index = result_data["stress_MPa"].idxmax()
    maximum_stress = float(result_data.loc[maximum_stress_index, "stress_MPa"])
    maximum_stress_time = float(result_data.loc[maximum_stress_index, "time_s"])
    exceeded_stress = result_data["stress_MPa"] > REFERENCE_STRESS_MPA
    exceeded_count = int(exceeded_stress.sum())

    plot_file = data_file.with_name(PLOT_FILE_NAME)
    figure, axes = plt.subplots()
    axes.plot(
        result_data["time_s"],
        result_data["stress_MPa"],
        marker="o",
        linestyle="-",
        label="Stress",
    )
    axes.scatter(
        result_data.loc[exceeded_stress, "time_s"],
        result_data.loc[exceeded_stress, "stress_MPa"],
        facecolors="none",
        edgecolors="orange",
        linewidths=2,
        s=100,
        zorder=4,
        label=f"Over {REFERENCE_STRESS_MPA:g} MPa ({exceeded_count})",
    )
    axes.scatter(
        maximum_stress_time,
        maximum_stress,
        color="red",
        zorder=5,
        label="Maximum stress",
    )
    axes.axhline(
        REFERENCE_STRESS_MPA,
        color="orange",
        linestyle="--",
        linewidth=1,
        label=f"Reference {REFERENCE_STRESS_MPA:g} MPa",
    )
    axes.annotate(
        f"{maximum_stress:g} MPa",
        (maximum_stress_time, maximum_stress),
        xytext=(8, 8),
        textcoords="offset points",
    )
    axes.set_xlabel("time(s)", fontsize=14)
    axes.set_ylabel("stress(MPa)", fontsize=14)
    axes.set_xlim(0, 10)
    axes.set_ylim(0, 9)
    axes.set_xticks(range(10))
    axes.set_yticks(range(10))
    axes.grid(True, color="lightgray", linewidth=0.8)
    axes.legend()
    figure.tight_layout()
    figure.savefig(plot_file)
    plt.close(figure)

    maximum_index = valid_data["force_N"].idxmax()
    maximum_force = float(valid_data.loc[maximum_index, "force_N"])
    maximum_time = float(valid_data.loc[maximum_index, "time_s"])
    return (
        len(valid_data),
        int(invalid_rows.sum()),
        maximum_force,
        maximum_time,
        maximum_stress,
        maximum_stress_time,
        exceeded_count,
    )


def main() -> None:
    data_file = find_data_file()
    (
        data_count,
        excluded_count,
        maximum_force,
        maximum_time,
        maximum_stress,
        maximum_stress_time,
        exceeded_count,
    ) = analyze_load_data(data_file)

    print(f"데이터 파일: {data_file.name}")
    print(f"데이터 개수: {data_count}개")
    print(f"유효한 데이터 수: {data_count}개")
    print(f"제외한 행수: {excluded_count}개")
    print(f"최대 하중: {maximum_force:g} N")
    print(f"해당 시간: {maximum_time:g} s")
    print(f"최대 응력: {maximum_stress:g} MPa")
    print(f"최대 응력 해당 시간: {maximum_stress_time:g} s")
    print(f"기준 응력 초과 데이터 개수: {exceeded_count}개")


if __name__ == "__main__":
    main()
