# -*- coding: utf-8 -*-

from __future__ import annotations
from datetime import datetime
from fart.utils import Colors
from io import TextIOWrapper
from os.path import dirname, realpath
from pathlib import Path
import sys
import threading
from types import CodeType, FrameType, ModuleType, TracebackType
from typing import Optional


class OutputStreamHook:
    """A custom output stream wrapper that can be used
    to redirect stdout and stderr.
    """

    __awaiting_newline: bool
    __origin: TextIOWrapper
    __iserror: bool
    __logfile: str
    __write_to_origin: bool
    __write_logs: bool

    def __init__(
        self: OutputStreamHook,
        origin: TextIOWrapper,
        is_error: bool,
        write_to_origin: bool,
        write_logs: bool,
    ) -> None:
        """Initializes the custom output stream.

        Parameters
        ----------
        origin : TextIOWrapper
            The original output stream.
        is_error : bool
            Whether the stream is an error stream.
        write_to_origin : bool
            Whether to write to the origin stream.
        write_logs : bool
            Whether to write to the log file.

        Returns
        -------
        None
        """
        log_dir: str
        log_file: str

        self.__awaiting_newline = False

        self.__origin = origin
        self.__iserror = is_error
        self.__write_to_origin = write_to_origin
        self.__write_logs = write_logs

        if not write_logs:
            return

        # Create the log directory
        log_dir = dirname(dirname(realpath(__file__))) + "/logs"
        Path(log_dir).mkdir(parents=True, exist_ok=True)

        log_file = datetime.now().strftime("%Y-%m-%d_%H-%M-%S.log")
        self.__logfile = log_dir + "/" + log_file
        Path(self.__logfile).touch(exist_ok=True)

    def write(self: OutputStreamHook, text: str) -> None:
        """Writes the text to the origin stream.

        Parameters
        ----------
        text : str

        Returns
        -------
        None
        """
        if not self.__awaiting_newline:
            text = self.__custom_format(text)
            self.__awaiting_newline = True

        self.__write(text)

        if text == "\n":
            self.__awaiting_newline = False

    def __write(self: OutputStreamHook, text: str) -> None:
        """Writes the text to the origin stream.

        Parameters
        ----------
        text : str

        Returns
        -------
        None
        """
        if self.__write_to_origin:
            self.__origin.write(text)
        if self.__write_logs:
            self.__log_to_file(text)

    def __log_to_file(self: OutputStreamHook, text: str) -> None:
        """Logs the text to a file.

        Parameters
        ----------
        text : str

        Returns
        -------
        None
        """
        # Strip the ANSI escape sequences
        for color in Colors.VALUES:
            text = text.replace(color, "")

        # Write the text to the file
        with open(self.__logfile, "a") as file:
            file.write(text)

    def __custom_format(self: OutputStreamHook, text: str) -> str:
        """Applies custom formatting to the text.

        Parameters
        ----------
        text : str

        Returns
        -------
        str - the formatted text
        """
        logger_name: str = "unknown"

        # Some simple formatting
        timestamp: str = datetime.now().strftime("%H:%M:%S")
        thread_name: str = threading.current_thread().name
        stream_name: str = ("stderr" if self.__iserror else "stdout").upper()

        # Get the file name and function name via the execution context
        # noinspection PyBroadException
        try:
            raise Exception()
        except Exception:
            trace_opt: Optional[TracebackType]
            trace: TracebackType
            frame_opt: Optional[FrameType]
            frame: FrameType
            code: CodeType
            # Hell. (because mypy is strict about Optional and optional
            #        chaining doesn't exist in Python)
            trace_opt = sys.exc_info()[2]
            if trace_opt is not None:
                trace = trace_opt
                frame_opt = trace.tb_frame
                if frame_opt is not None:
                    frame = frame_opt
                    frame_opt = frame.f_back
                    if frame_opt is not None:
                        frame = frame_opt
                        frame_opt = frame.f_back
                        if frame_opt is not None:
                            code = frame_opt.f_code
                            logger_name = f"{Path(code.co_filename).stem}.py/{code.co_name}"
            # End of hell.

        # Append the text to the output
        output = Colors.LIGHT_RED if self.__iserror else Colors.RESET
        output += f"[{timestamp}] "
        output += f"[{stream_name}/{thread_name}] "
        output += f"[{logger_name}]: "
        output += Colors.RESET
        output += text
        return output

    def flush(self: OutputStreamHook) -> None:
        """Flushes the origin stream.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        self.__origin.flush()

    @staticmethod
    def apply(
        target: ModuleType,
        stream_attr_name: str,
        is_error: bool = False,
        write_to_console: bool = False,
        write_logs: bool = True,
    ) -> None:
        """Replaces the provided output stream with a custom one.

        Parameters
        ----------
        target : ModuleType
            The target module.
        stream_attr_name : str
            The name of the output stream attribute.
        is_error : bool
            Whether the stream is an error stream.
        write_to_console : bool
            Whether to write to the console.
        write_logs : bool
            Whether to write to the log file.

        Returns
        -------
        None
        """
        setattr(
            target,
            stream_attr_name,
            OutputStreamHook(
                getattr(target, stream_attr_name), is_error, write_to_console, write_logs
            ),
        )
