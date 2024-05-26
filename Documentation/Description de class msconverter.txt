"""
Classe MSCONSConverter
======================

Une classe pour convertir les fichiers de données MSCONS au format CSV. Cette classe permet de lire les fichiers MSCONS,
de les analyser et de les convertir au format CSV prédéfini. Les fichiers CSV générés sont enregistrés
dans un répertoire spécifié.

Attributs
---------
target_dir : str
    Répertoire où les fichiers CSV de sortie seront enregistrés.
logger : CustomLogger
    Journal pour enregistrer les messages de débogage, d'information, d'avertissement et d'erreur.

Méthodes
--------
to_csv(data: dict, csv_header_values: list)
    Convertit les données fournies en un fichier CSV avec les valeurs d'en-tête spécifiées.
parse_mscons(file_name: str) -> dict
    Analyse le fichier MSCONS et retourne les données sous forme de dictionnaire.
convert_to_csv(file_name: str, csv_header_values: list)
    Analyse le fichier MSCONS et convertit les données en un fichier CSV avec les valeurs d'en-tête spécifiées.
__parse_date_to_csv(input_date: str, format_date: str = "303") -> str
    Analyse la date au format MSCONS pour la rendre compatible avec le format CSV.
__verify_single_entry(entry_line: str, csv_header_values: list) -> None
    Vérifie la cohérence de chaque ligne CSV lors de la création.
__read_file_content(file_name: str) -> str
    Lit le contenu du fichier spécifié.
"""

import os
from datetime import datetime

from msconsconverter.constants import CSV_DELIMITER, CSV_FILE_PREFIX, VERIFY
from msconsconverter.exceptions import EntryHeaderCSVConflict
from msconsconverter.helpers import gen_file_name
from msconsconverter.logger import CustomLogger


class MSCONSConverter:
    """
    Une classe utilisée pour convertir les données MSCONS en format CSV.

    ...

    Attributs
    ---------
    target_dir : str
        Le répertoire où les fichiers CSV de sortie seront enregistrés.
    logger : CustomLogger
        Journal pour enregistrer les messages de débogage, d'information, d'avertissement et d'erreur.

    Méthodes
    --------
    to_csv(data: dict, csv_header_values: list):
        Convertit les données fournies en un fichier CSV avec les valeurs d'en-tête spécifiées.
    parse_mscons(file_name: str) -> dict:
        Analyse le fichier MSCONS et retourne les données sous forme de dictionnaire.
    convert_to_csv(file_name: str, csv_header_values: list):
        Analyse le fichier MSCONS et convertit les données en un fichier CSV avec les valeurs d'en-tête spécifiées.
    __parse_date_to_csv(input_date: str, format_date: str = "303") -> str:
        Analyse la date au format MSCONS pour la rendre compatible avec le format CSV.
    __verify_single_entry(entry_line: str, csv_header_values: list) -> None:
        Vérifie la cohérence de chaque ligne CSV lors de la création.
    __read_file_content(file_name: str) -> str:
        Lit le contenu du fichier spécifié.
    """

    def __init__(self, target_dir=None, logger=None):
        """
        Construit tous les attributs nécessaires pour l'objet MSCONSConverter.

        Paramètres
        ----------
            target_dir : str
                Répertoire où les fichiers CSV de sortie seront enregistrés.
            logger : CustomLogger
                Journal pour enregistrer les messages de débogage, d'information, d'avertissement et d'erreur.
        """
        self.logger = logger
        self.logger.debug('class "MSCONSConverter" a été créée')

        if not os.path.exists(target_dir):
            raise Exception(f"Aucun dossier de sortie trouvé : {target_dir}")

        self.target_dir = target_dir

    def to_csv(self, data: dict, csv_header_values: list):
        """
        Convertit les données fournies en un fichier CSV avec les valeurs d'en-tête spécifiées.

        Paramètres
        ----------
        data : dict
            Données à enregistrer.
        csv_header_values : list
            En-tête du fichier CSV.

        Exceptions
        ----------
        RuntimeError
            Si une erreur se produit pendant le processus de conversion.
        """
        new_file_name = "{0}-{1}".format(CSV_FILE_PREFIX, gen_file_name(extension=".csv"))
        new_file_name_path = os.path.join(self.target_dir, new_file_name)

        csv = open(new_file_name_path, "w")
        csv.write(CSV_DELIMITER.join(csv_header_values) + "\n")

        for loc_mscons in data["loc_mscons"]:
            loc_mscons_plz = loc_mscons[8:13]
            loc_mscons_eegkey = loc_mscons[-20:]
            # évaluation des résultats de l'analyse
            loc_to_expect = loc_mscons[:8] + loc_mscons_plz + loc_mscons_eegkey
            if loc_mscons != loc_to_expect:
                self.logger.warning(
                    f"format LOC personnalisé inattendu, attendu : {loc_mscons} ; trouvé : {loc_to_expect}"
                )

            tmp_line = ""
            for item in data["qty"][loc_mscons]:

                tmp_line = '"{0}"{1}'.format(loc_mscons, CSV_DELIMITER)
                tmp_line += '"{0}"{1}'.format(loc_mscons_plz, CSV_DELIMITER)
                tmp_line += '"{0}"{1}'.format(loc_mscons_eegkey, CSV_DELIMITER)
                tmp_line += "{0}{1}".format(self.__parse_date_to_csv(item[1]), CSV_DELIMITER)
                tmp_line += "{0}{1}".format(self.__parse_date_to_csv(item[2]), CSV_DELIMITER)
                tmp_line += '"{0}"'.format(item[0])
                tmp_line += "\n"

                if VERIFY:
                    self.__verify_single_entry(tmp_line, csv_header_values)

                csv.write(tmp_line)

        csv.close()

        self.logger.debug(f"résultats de l'analyse enregistrés dans le fichier : {new_file_name_path}")

    def parse_mscons(self, file_name: str) -> dict:
        """
        Analyse le format MSCONS.

        Paramètres
        ----------
        file_name : str
            Nom du fichier à analyser.

        Retours
        -------
        dict
            Un dictionnaire contenant les données analysées.
        """
        mscons_dict = {}
        mscons_data = self.__read_file_content(file_name)

        self.logger.debug("caractères spéciaux du MSCONS identifiés")

        COMPONENT_SEPARATOR = ":"
        ELEMENT_SEPARATOR = "+"
        DECIMAL_MARK = "."
        RELEASE_SYMBOL = "?"
        SEGMENTAION_SYMBOL = "'"

        if mscons_data.startswith("UNA"):
            offset = 2
            COMPONENT_SEPARATOR = mscons_data[offset + 1]
            ELEMENT_SEPARATOR = mscons_data[offset + 2]
            DECIMAL_MARK = mscons_data[offset + 3]
            RELEASE_SYMBOL = mscons_data[offset + 4]
            SEGMENTAION_SYMBOL = mscons_data[offset + 6]
        else:
            self.logger.debug("aucun caractère spécial trouvé, les valeurs par défaut seront utilisées")

        self.MSCONS_DECIMAL_MARK = DECIMAL_MARK

        self.logger.debug(
            f"""\nSymboles spéciaux qui seront utilisés
            COMPONENT_SEPARATOR {COMPONENT_SEPARATOR}
            ELEMENT_SEPARATOR {ELEMENT_SEPARATOR}
            DECIMAL_MARK {self.MSCONS_DECIMAL_MARK}
            RELEASE_SYMBOL {RELEASE_SYMBOL}
            SEGMENTAION_SYMBOL {SEGMENTAION_SYMBOL}"""
        )

        mscons_tokens = mscons_data.split(SEGMENTAION_SYMBOL)
        cur_qty = 0.0
        start_saving = False
        save_cur_qty_value = False

        current_loc = None

        for index, token in enumerate(mscons_tokens):
            if token.startswith("LOC"):
                subtoken = token.split(ELEMENT_SEPARATOR)
                self.logger.debug(subtoken)
                if subtoken[1] == "172":
                    if "loc_mscons" not in mscons_dict:
                        mscons_dict["loc_mscons"] = list()
                    mscons_dict["loc_mscons"].append(subtoken[2])
                    current_loc = subtoken[2]

                self.logger.debug(f"Jeton LOC trouvé {subtoken} à la ligne : {index}")

            if token.startswith("PIA"):
                self.logger.warning("PIA trouvé, mais ignoré")

            if token.startswith("QTY"):
                start_saving = True
                subcomponents = token.split(COMPONENT_SEPARATOR)
                if subcomponents[0] == "QTY+220":
                    cur_qty = subcomponents[1]
                else:
                    self.logger.warning("code numérique étrange pour QTY trouvé, la valeur sera enregistrée comme 0.0")
                    cur_qty = 0.0

            if token.startswith("DTM"):
                subcomponents = token.split(COMPONENT_SEPARATOR)
                subcomponents[1] = subcomponents[1].replace(RELEASE_SYMBOL, "")

                if subcomponents[0] == "DTM+163":
                    cur_date_period_start = subcomponents[1]

                if subcomponents[0] == "DTM+164":
                    cur_date_period_end = subcomponents[1]
                    save_cur_qty_value = True

                if subcomponents[2] != "303":
                    self.logger.warning("format de date différent")

            if save_cur_qty_value and start_saving:
                if "qty" not in mscons_dict:
                    mscons_dict["qty"] = {}

                if current_loc not in mscons_dict["qty"]:
                    mscons_dict["qty"][current_loc] = []

                mscons_dict["qty"][current_loc].append(
                    (
                        cur_qty,
                        cur_date_period_start,
                        cur_date_period_end,
                    )
                )

                save_cur_qty_value = False
                start_saving = False

        self.logger.debug(f"Data analysée : {mscons_dict}")
        return mscons_dict

    def convert_to_csv(self, file_name: str, csv_header_values: list):
        """
        Analyse le fichier MSCONS et convertit les données en un fichier CSV avec les valeurs d'en-tête spécifiées.

        Paramètres
        ----------
        file_name : str
            Nom du fichier à analyser.
        csv_header_values : list
            En-tête du fichier CSV.
        """
        parsed_data = self.parse_mscons(file_name)
        self.logger.debug(f"Données analysées obtenues : {parsed_data}")
        self.to_csv(parsed_data, csv_header_values)

    def __parse_date_to_csv(self, input_date: str, format_date: str = "303") -> str:
        """
        Analyse la date au format MSCONS pour la rendre compatible avec le format CSV.

        Paramètres
        ----------
        input_date : str
            Date à analyser.
        format_date : str, optionnel
            Format de la date, par défaut "303".

        Retours
        -------
        str
            Date analysée au format CSV.
        """
        if format_date != "303":
            self.logger.warning("la date obtenue n'est pas en format 303")

        parsed_date = datetime.strptime(input_date, "%Y%m%d").strftime("%d.%m.%Y")
        self.logger.debug(f"Date analysée {input_date} en {parsed_date}")

        return parsed_date

    def __verify_single_entry(self, entry_line: str, csv_header_values: list) -> None:
        """
        Vérifie la cohérence de chaque ligne CSV lors de la création.

        Paramètres
        ----------
        entry_line : str
            Ligne à vérifier.
        csv_header_values : list
            En-tête du fichier CSV.

        Exceptions
        ----------
        EntryHeaderCSVConflict
            Si la ligne d'entrée ne correspond pas à l'en-tête du CSV.
        """
        if len(entry_line.split(CSV_DELIMITER)) != len(csv_header_values):
            raise EntryHeaderCSVConflict

    def __read_file_content(self, file_name: str) -> str:
        """
        Lit le contenu du fichier spécifié.

        Paramètres
        ----------
        file_name : str
            Nom du fichier à lire.

        Retours
        -------
        str
            Contenu du fichier.
        """
        with open(file_name, "r") as f:
            content = f.read()

        self.logger.debug(f"le fichier {file_name} a été lu avec succès")
        return content
