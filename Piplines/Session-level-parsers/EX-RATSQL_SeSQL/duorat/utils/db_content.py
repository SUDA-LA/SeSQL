import os
import re
import sqlite3
from enum import Enum, auto
from typing import Dict, List, Set, Tuple, Iterable
import json
from dataclasses import dataclass

from nltk import PorterStemmer
from nltk.corpus import stopwords

stemmer = PorterStemmer()


@dataclass(frozen=True)
class ColumnIdentifier:
    db_id: str
    table_name: str
    column_name: str


class EntryType(Enum):
    # a whole DB row
    WHOLE_ENTRY = auto()
    # one word from a DB row (a DB row with a single word will count as both whole and partial)
    PARTIAL_ENTRY = auto()


Entry = Tuple[Tuple[str, ...], EntryType]

stop_words = set(stopwords.words("english")).union({".", "?", ","})
# map: (span, entry_type) -> {column_that_matches: value}
_db_index: Dict[Entry, Dict[ColumnIdentifier, str]] = {}
# set of indexed columns
_indexed_columns: Set[ColumnIdentifier] = set()


def match_db_content(
    span: List[str],
    column_name: str,
    table_name: str,
    db_id: str,
    all_db_content_dic: dict,
    with_stemming: bool,
) -> List[Tuple[EntryType, str]]:
    """
    Try to match a span to a certain database column.
    Indexes the column beforehand if it was not indexed yet.
    :param span:
    :param column_name:
    :param table_name:
    :param db_id:
    :param db_path:
    :param with_stemming:
    :return: List of matches of length 0, 1 or 2.
    A match is defined by a tuple (entry_type, match_value) giving the type of entry (whole or partial), and the
    raw DB-value that was matched.
    """

    def _index_column(columnd_identifier: ColumnIdentifier, all_db_content_dic: dict) -> None:
        """
        Go through column content and add each row and its words to the index
        """
        if columnd_identifier in _indexed_columns:
            return  # column was already indexed
        
        column_content = get_column_content_from_file(columnd_identifier,all_db_content_dic)
        #column_content = get_column_content(columnd_identifier, db_path)
        # index the row and the words in it
        for row in column_content:
            processed_row = pre_process_words(
                words=row.lower().split(), with_stemming=with_stemming
            )

            # TODO: What if several rows in the same column produce the same entry ("James Doe" and "James Smith"
            # both would have "James" part-of-entry). List of matching values instead?
            # Add the whole row
            entry: Entry = (processed_row, EntryType.WHOLE_ENTRY)
            if entry not in _db_index:
                _db_index[entry] = {}
            _db_index[entry][columnd_identifier] = row

            # Add parts of the row
            # TODO: also add sub-spans of length >1 ?
            for word in processed_row:
                entry: Entry = ((word,), EntryType.PARTIAL_ENTRY)
                if entry not in _db_index:
                    _db_index[entry] = {}
                _db_index[entry][columnd_identifier] = row

        # register that column was indexed
        _indexed_columns.add(columnd_identifier)

    # Skip stop-words
    if len(span) == 1 and span[0] in stop_words:
        return []

    span = pre_process_words(words=span, with_stemming=with_stemming)
    column_identifier = ColumnIdentifier(
        column_name=column_name, table_name=table_name, db_id=db_id
    )
    _index_column(
        columnd_identifier=column_identifier, all_db_content_dic=all_db_content_dic,
    )

    matches: List[Tuple[EntryType, str]] = []
    for entry in ((span, EntryType.WHOLE_ENTRY), (span, EntryType.PARTIAL_ENTRY)):
        if entry in _db_index and column_identifier in _db_index[entry]:
            matches.append((entry[1], _db_index[entry][column_identifier]))
    return matches


def get_tables_content(db_path):
    final_all_db_content_dic={}
    with open(db_path,"r",encoding="utf-8") as db_content:
        db_table_content=json.load(db_content)
        for database in db_table_content:
            db_id=database["db_id"]
            tables=database["tables"]
            database_content_dict={}
            for table_name in tables:
                table_content=tables[table_name]["cell"]
                column_name_lst=tables[table_name]["header"]
                table_content_dict={}
                for column_id in range(len(column_name_lst)):
                    colume_content_lst=[]
                    for cell in table_content:
                        colume_content_lst.append(cell[column_id])
                    table_content_dict[column_name_lst[column_id]]=colume_content_lst
                database_content_dict[table_name]=table_content_dict
            final_all_db_content_dic[db_id]=database_content_dict
    return final_all_db_content_dic
                    




def get_column_content_from_file(column_identifier: ColumnIdentifier, all_db_content: dict) -> List[str]:
    column_name=column_identifier.column_name
    table_name=column_identifier.table_name
    db_id=column_identifier.db_id
    return all_db_content[db_id][table_name][column_name]



def get_column_content(column_identifier: ColumnIdentifier, db_path: str) -> List[str]:
    """Obtain and process content of column"""
    db_file = db_path
    conn = sqlite3.connect(db_file)
    # Avoid "could not decode to utf-8" errors
    conn.text_factory = lambda b: b.decode(errors="ignore")
    query = f'SELECT "{column_identifier.column_name}" FROM "{column_identifier.table_name}";'
    try:
        col_content = conn.execute(query).fetchall()
    except:
        col_content = []
    conn.close()

    col_content = [r[0] for r in col_content]
    processed_column_content = [str(row) for row in col_content]
    return processed_column_content


def pre_process_words(words: Iterable[str], with_stemming: bool) -> Tuple[str, ...]:
    if with_stemming:
        return tuple(stemmer.stem(w) for w in words)
    else:
        return tuple(words)
