custom_latex_md_dict = {
    "KMOS3D": r"KMOS$^{\hbox{\textit{{\scriptsize{3D}}}}}$",
    "NOEMA3D": r"NOEMA$^{\hbox{\textit{{\scriptsize{3D}}}}}$",
    "pndsign": r"\#",
}

custom_html_md_dict = {
    "KMOS3D": r"KMOS<sup>3D</sup>",
    "NOEMA3D": r"NOEMA<sup>3D</sup>",
    "pndsign": r"#",
}


custom_lastname_fix_dict = {
    "NMFS": {
        "list": ["Forster", "Förster", "Foerster"],
        "last_match": "Schreiber",
        "last_replace": "Förster",
    },
}
