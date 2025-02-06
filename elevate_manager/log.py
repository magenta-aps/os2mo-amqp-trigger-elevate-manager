# SPDX-FileCopyrightText: Magenta ApS
#
# SPDX-License-Identifier: MPL-2.0
import logging

import structlog  # type: ignore


def setup_logging(log_level_name: str) -> None:
    _log_level_value = logging.getLevelName(log_level_name)

    structlog.configure(
        wrapper_class=structlog.make_filtering_bound_logger(_log_level_value)
    )
