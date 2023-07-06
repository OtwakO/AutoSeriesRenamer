# -*- coding: utf-8 -*-
import os, sys, time, re
import renamer_module, natsort
import click, pathlib, shutil
from loguru import logger
from decouple import config

os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))

logger.add(
    "logs/output.log",
    format="[{time:YYYY-MM-DD hh:mm:ss A}] | {level} | {message}",
    rotation="20 MB",
)

FILE_FORMAT_FILTER = config("FILE_FORMAT_FILTER")
REGEX_FILTER = config("REGEX_FILTER")


@click.command()
@click.option(
    "-d",
    "--directory",
    required=True,
    prompt="Enter directory",
    type=str,
    help=r"Run on directory of the series.",
)
def single_directory(directory):
    absolute_path = os.path.abspath(rf"{directory}")
    if not os.path.exists(absolute_path):
        logger.error(f"{absolute_path} does not exist.")
        os._exit(0)
    else:
        logger.info(f"Directory: {absolute_path}")
        logger.info(f"Renaming files...")

    if len(os.listdir(absolute_path)) == 0:
        logger.error(f"Folder is empty.")
        os._exit(0)
    file_list = natsort.natsorted(os.listdir(absolute_path))
    query_list = [os.path.splitext(filename)[0] for filename in file_list]
    rename_series = renamer_module.rename_series(query_list)

    for index, file in enumerate(file_list):
        os.rename(
            f"{absolute_path}/{file}",
            f"{absolute_path}/{rename_series[index]}{os.path.splitext(file)[-1]}",
        )
        logger.success(f"{file} --> {rename_series[index]}{os.path.splitext(file)[-1]}")
    logger.success(f"Renaming finished.")


@click.command()
@click.option(
    "-s",
    "--scan_directory",
    required=True,
    prompt="Enter directory",
    type=str,
    help=rf"Scan a directory and rename all files that fit the format",
)
def scan_directory(scan_directory):
    absolute_path = os.path.abspath(rf"{scan_directory}")
    if not os.path.exists(absolute_path):
        logger.error(f"{absolute_path} does not exist.")
        os._exit(0)
    else:
        logger.info(f"Scanning directory: {absolute_path}")

    if len(os.listdir(absolute_path)) == 0:
        logger.error(f"Folder is empty.")
        os._exit(0)

    # Search through files for files needing to renaming
    file_ext_list = []
    root_path_list = []
    file_list = []
    for root, dirs, files in os.walk(absolute_path, topdown=False):
        for file in files:
            if os.path.splitext(file)[-1] in FILE_FORMAT_FILTER:
                # Skip already renamed
                if not re.search(REGEX_FILTER, file, re.IGNORECASE):
                    file_ext_list.append(os.path.splitext(file)[-1])
                    file_list.append(os.path.splitext(file)[0])
                    root_path_list.append(root)

    # Get new file names
    if file_list:
        gpt_response = renamer_module.rename_series(file_list)

        # Add .extension back to file lists
        file_list = [
            basename + extension
            for basename, extension in zip(file_list, file_ext_list)
        ]

        gpt_response = [
            basename + extension
            for basename, extension in zip(gpt_response, file_ext_list)
        ]

        rename_logger = list(zip(file_list.copy(), gpt_response.copy()))

        # Add path back to file lists
        file_list = [
            os.path.join(path, filename)
            for path, filename in zip(root_path_list, file_list)
        ]

        gpt_response = [
            os.path.join(path, filename)
            for path, filename in zip(root_path_list, gpt_response)
        ]

        # Rename all files to GPT response filename
        rename_query = list(zip(file_list, gpt_response))
        for filename_pair in rename_query:
            os.rename(*filename_pair)

        for logging_pair in rename_logger:
            logger.success(f"{logging_pair[0]} --> {logging_pair[-1]}")
    else:
        pass
        # logger.info(f"No files needed for rename.")
        # os._exit(0)

    # Move all files to proper folders if already named properly
    for root, dirs, files in os.walk(absolute_path, topdown=False):
        for file in files:
            if os.path.splitext(file)[-1] in FILE_FORMAT_FILTER:
                # if already named properly
                if re.search(REGEX_FILTER, file, re.IGNORECASE):
                    if (
                        "Season" in os.path.split(root)[-1]
                    ):  # Existing season name found
                        series_name = os.path.split(os.path.split(root)[0])[-1]
                        new_file_name = f"{series_name}{re.search(REGEX_FILTER, file).group(0)}{os.path.splitext(file)[-1]}"
                        current_series_name = re.sub(
                            REGEX_FILTER, "", os.path.splitext(file)[0], re.IGNORECASE
                        )
                        if series_name != current_series_name:
                            os.rename(
                                os.path.join(root, file),
                                os.path.join(root, new_file_name),
                            )
                            logger.success(f"{file} --> {new_file_name}")
                    else:
                        series_name = re.sub(
                            REGEX_FILTER, "", os.path.splitext(file)[0], re.IGNORECASE
                        )
                    season_number = int(
                        re.search(
                            r"S(\d+)E", os.path.splitext(file)[0], re.IGNORECASE
                        ).group(1)
                    )
                    destination = os.path.normpath(
                        f"{absolute_path}/{series_name}/Season {season_number}"
                    )
                    pathlib.Path(destination).mkdir(parents=True, exist_ok=True)
                    if destination != os.path.normpath(os.path.join(root)):
                        if not os.path.exists(f"{destination}/{file}"):
                            shutil.move(
                                os.path.join(root, file),
                                f"{destination}/{file}",
                            )
                            logger.success(
                                f"Moving file: {os.path.join(root, file)} --> {os.path.normpath(f'{destination}/{file}')}"
                            )
                        else:
                            logger.error(
                                f"File exists in destination! {os.path.join(root, file)} skipped."
                            )

        # Remove all empty directories
        for root, dirs, files in os.walk(absolute_path, topdown=False):
            if len(os.listdir(root)) == 0:
                os.rmdir(root)
                logger.success(f"Directory {os.path.join(root)} is empty, removing...")

    logger.success(f"Execution finished.")


@click.group()
def cli_commands():
    pass


cli_commands.add_command(single_directory)
cli_commands.add_command(scan_directory)

if __name__ == "__main__":
    cli_commands()
