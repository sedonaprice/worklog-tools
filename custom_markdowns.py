import copy

custom_latex_md_dict = {
    "KMOS3D": r"KMOS$^{\hbox{\textit{{\scriptsize{3D}}}}}$",
    "NOEMA3D": r"NOEMA$^{\hbox{\textit{{\scriptsize{3D}}}}}$",
    "pndsign": r"\#",
    "\$": "$",
    r"{\alpha}": r"{\ensuremath{\alpha}}",
    r"\{\textbackslash{}alpha\}": r"{\ensuremath{\alpha}}",
    r"{\lesssim}": r"{\ensuremath{\lesssim}}",
    r"\{\textbackslash{}lesssim\}": r"{\ensuremath{\lesssim}}",
    "\~": r"\ensuremath{\sim}",
    r"\textbackslash{}sim": r"\ensuremath{\sim}",
    "\{sim\}": r"\ensuremath{\sim}",
    " sim ": r"\ensuremath{\sim}",
    r"\{\textbackslash{}tilde\}": r"\ensuremath{\sim}",
    "\\approx": r"\ensuremath{\approx}",
    r"\textbackslash{}tilde": r"\ensuremath{\sim}",
    r"{\ensuremath{\sim}}": r"\ensuremath{\sim}",
    r"\{\}": "",
}


custom_html_md_dict = {
    "KMOS3D": r"KMOS<sup>3D</sup>",
    "NOEMA3D": r"NOEMA<sup>3D</sup>",
    "pndsign": r"#",
    r"{\alpha}": "\u03b1",
    r"{\lesssim}": "\u2272",
    r"--": r"-",
    "$": r"",
    r"\sim": r"~",
    r"{\tilde}": r"~",
    r"\tilde": r"~",
    r"{}": "",
}

custom_markdown_md_dict = copy.deepcopy(custom_html_md_dict)
custom_markdown_md_dict[r"~"] = r"\~"


custom_lastname_fix_dict = {
    "NMFS": {
        "list": ["Forster", "Förster", "Foerster"],
        "last_match": "Schreiber",
        "last_replace": "Förster",
    },
}
