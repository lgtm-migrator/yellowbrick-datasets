# ybdata.validate
# Helper functions and checks for performing validation on a dataset.
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Mon Dec 31 08:00:36 2018 -0500
#
# For license information, see LICENSE.txt
#
# ID: validate.py [] benjamin@bengfort.com $

"""
Helper functions and checks for performing validation on a dataset.
"""

##########################################################################
## Imports
##########################################################################

import os
import json

from glob import glob


##########################################################################
## Utilities
##########################################################################

def exists_in_dataset(root, *path):
    """
    Checks if the specified path (joined by os-specific sep) exists in the
    path specified by the root directory.
    """
    return os.path.exists(os.path.join(root, *path))


def standard_package_checklist(path, include_optional=False):
    """
    Given the path to a dataset directory, return a dictionary checklist of
    validators associated with the standard dataset package model.

    Parameters
    ----------
    path : str
        Path to the dataset directory on disk, usually in fixtures

    include_optional : bool, default=False
        Include optional checklist parameters in return

    Returns
    -------
    checklist : dict
        Maps checklist items to bools if they are checked or not
    """
    name = os.path.basename(path)

    # Base Checklist
    checklist = {
        "has readme": exists_in_dataset(path, "README.md"),
        "has metadata": exists_in_dataset(path, "meta.json"),
        "has pandas dataset": exists_in_dataset(path, name + ".csv.gz"),
        "has numpy dataset": exists_in_dataset(path, name + ".npz"),
    }

    if include_optional:
        checklist.update({
            "has citation": exists_in_dataset(path, "citation.bib")
        })

    # Metadata checklist
    if exists_in_dataset(path, "meta.json"):
        with open(os.path.join(path, "meta.json")) as f:
            try:
                meta = json.load(f)
                checklist["meta is valid json"] = True
            except:
                meta = {}
                checklist["meta is valid json"] = False

        checklist.update({
            "meta has features": "features" in meta,
            "meta has target": "target" in meta,
        })

        if include_optional:
            checklist.update({
                "meta has class labels": "labels" in meta,
                "meta has alternate targets": "alternate_targets" in meta,
            })

    return checklist


def is_valid_standard(path, raise_for_invalid=False):
    """
    Returns True if the standard dataset is valid and ready for upload.
    """
    valid = all(standard_package_checklist(path, include_optional=False).values())
    if raise_for_invalid and not valid:
        raise ValueError("The dataset at '{}' is not valid".format(path))
    return valid


def corpus_package_checklist(path, include_optional=False):
    """
    Given the path to a dataset directory, return a dictionary checklist of
    validators associated with the corpus dataset package model.

    Parameters
    ----------
    path : str
        Path to the dataset directory on disk, usually in fixtures

    include_optional : bool, default=False
        Include optional checklist parameters in return

    Returns
    -------
    checklist : dict
        Maps checklist items to bools if they are checked or not
    """
    checklist = {
        "has readme": exists_in_dataset(path, "README.md"),
        "has subdirectory categories": all([os.path.isdir(p) for p in glob(os.path.join(path, "*")) if not p.endswith(".md")]),
        "has plaintext data": len(glob(os.path.join(path, "*/*.txt"))) > 0,
        "no data in root": len(glob(os.path.join(path, "*.txt"))) == 0,
    }

    if include_optional:
        checklist.update({
            "has citation": exists_in_dataset(path, "citation.bib")
        })

    return checklist


def is_valid_corpus(path, raise_for_invalid=False):
    """
    Returns True if the corpus dataset is valid and ready for upload.
    """
    valid = all(corpus_package_checklist(path, include_optional=False).values())
    if raise_for_invalid and not valid:
        raise ValueError("The corpus at '{}' is not valid".format(path))
    return valid