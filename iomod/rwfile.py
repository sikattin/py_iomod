#-------------------------------------------------------------------------------
# Name:        delete_null_row.py
# Purpose:     テキストファイルを読み込み、空白行を削除した文字列リストを返す。
#
# Author:      shikano.takeki
#
# Created:     08/12/2017
# Copyright:   (c) shikano.takeki 2017
# Licence:     <your licence>
#-------------------------------------------------------------------------------
# -*- coding: utf-8 -*-
import os
import re
import codecs
import json


SQL_COMMENT_SINGLE = "--"
SQL_COMMENT_MULTI_START = "/\*"
SQL_COMMENT_MULTI_END = "\*/"
SQL_DELIMITER = ";"
SQL_DELIMITER_STATEMENT = "DELIMITER"

class RWFile:
    """RWFile"""

    def __init__(self):
        """コンストラクタ

        :param encode: 文字エンコーディング.
        """
        self.list_str = list()
        self.with_combined = ''

    def read_text_file(self, dir_path: str, encode=None):
        """ファイルを読み込んで空白行を削除した文字列群をリストに格納し返す.

        行頭が -, #, /* で始まる行(コメント行)の場合は、その行は返却するリストに含めない。

        :param dir_path: ディレクトリパス.
        :param encode: 文字エンコーディングの指定 デフォルトはUTF-8.
        """
        comment_flag = False
        if encode is None:
            encode = 'utf_8'
        # 挿入文字列を格納しておくリスト
        ins_str = list()
        # 区切り文字
        delimiter = ";"
        # 連結用文字列を格納しておく.
        joined_strs = ''
        try:
            with codecs.open(dir_path, mode='r', encoding=encode) as file:
                for line in file:
                    if line in {'\n', '\r', '\r\n'}:
                        continue
                    elif self.is_matched(line=line.rstrip(), search_objs=["^-+", "^#+"]):
                        continue
                    elif self.is_matched(line=line.rstrip(), search_objs=["^(/\*).*(\*/)$"]):
                        continue
                    elif self.is_matched(line=line.rstrip(), search_objs=["^/\*"]) \
                        and comment_flag is False:
                        comment_flag = True
                        continue
                    elif self.is_matched(line=line.rstrip(), search_objs=["\*/$"]) \
                        and comment_flag is True:
                        comment_flag = False
                        continue
                    elif comment_flag is True:
                        continue
                    else:
                        joined_strs = self.join_lines(line=line, delimiter=delimiter)
                        if not len(joined_strs) == 0:
                            ins_str.append(joined_strs)
                        """
                        joined_str += (line.rstrip().split(),)
                        if not line.rstrip()[-1] == ';':
                            continue
                        for list_element in joined_str:
                            joined_strs += ' '.join(list_element) + ' '
                        print("joined_strs = {}".format(joined_strs))
                        ins_str.append(joined_strs.rstrip())
                        joined_str = tuple()
                        joined_strs = ''
                        """
        except FileNotFoundError as e:
            print("\n存在しないファイルです。パス指定が正しいかどうか確認してください。\n")
            raise e
        except UnicodeError as e:
            print("\nエラー原因: " + e.reason)
            print("文字エンコーディングの指定を変更してみるといいかもしれない\n")
            raise e
        except (LookupError, ValueError) as e:
            print("存在しない、または無効な値です。")
            raise e
        else:
            return ins_str

    def read_text(self, path: str, encoding=None):
        """
        テキストファイルの内容を1行1要素としてタプルで返す。
        ただし、空白行 及び コメント行を除く。

        Args:
            param1 path[str]: 読み込むテキストファイルのパス。
            param2 encoding[str]: 読み込み時のエンコード文字。デフォルトは utf8

        Returns:
            tuple()

        Raises:
            FileNotFoundError
            UnicodeError
            LookupError
            ValueError
        """
        ret = tuple()
        comment_flag = False
        # make regular expressions.
        regexp_singlecomment = "^{}+".format(SQL_COMMENT_SINGLE)
        regexp_multicomment = "^({0}).*({1})$".format(SQL_COMMENT_MULTI_START,
                                                      SQL_COMMENT_MULTI_END)
        regexp_multicomment_start = "^{}".format(SQL_COMMENT_MULTI_START)
        regexp_multicomment_end = "{}$".format(SQL_COMMENT_MULTI_END)

        if encoding is None:
            encoding = 'utf_8'

        if self.is_utf8_with_bom(path):
            encoding = 'utf-8-sig'
        else:
            encoding = 'utf_8'
        try:
            with codecs.open(r"{}".format(path), mode="r", encoding=encoding) as f:
                for line in f:
                    # 改行文字のみの行は空行とみなす。
                    if line in {'\n', '\r', '\r\n'}:
                        continue
                    # 複数行のコメント中(comment_flag = Trueのとき)は返却リストに含めない。
                    elif comment_flag is True:
                        continue
                    elif self.is_matched(line=line.rstrip(), search_objs=[regexp_singlecomment]):
                        continue
                    # 複数行コメントが開始したとみなされたとき、commnet_flag を True に設定している
                    elif self.is_matched(line=line.rstrip(), search_objs=[regexp_multicomment_start]) \
                        and comment_flag is False:
                        comment_flag = True
                        continue
                    # 複数行コメントが終了したとみなされたとき、comment_flag を False に設定している
                    elif self.is_matched(line=line.rstrip(),
                                         search_objs=[regexp_multicomment_end]) \
                    and comment_flag is True:
                        comment_flag = False
                        continue
                    elif self.is_matched(line=line.rstrip(), search_objs=[regexp_multicomment]):
                        continue
                    else:
                        # コメント行 及び 空行 以外だった時の処理
                        ret += (line.rstrip(), )
        except FileNotFoundError as filenot_e:
            print("\n存在しないファイルです。ファイルパスが正しいかどうか確認してください。\n")
            raise filenot_e
        except UnicodeError as unicode_e:
            print("\nエラー原因: " + unicode_e.reason)
            print("エンコードエラーです。正しい文字コードを指定してください。")
            raise unicode_e
        except (LookupError, ValueError) as e:
            print("存在しない, または無効な値です。")
            raise e
        except:
            raise
        else:
            return ret

    def get_queries_from_lines(self, lines: tuple, delimiter=None):
        """
        delimiter を区切り文字として、1クエリーを1要素としてタプルで返す。
        このメソッドは、read_text() の戻り値を linesのパラメータとして使用することを
        想定されて作られています。

        SELECT ~
        JOIN ~
        JOIN ~
        WHERE {delimiter}
        INSERT ~{delimiter}

        上記のような内容であれば、
        ('SELECT ~ JOIN ~ JOIN ~ WHERE{delimiter}', 'INSERT ~{delimiter}')
        のようなタプルにして返却する。

        Args:
            param1 lines: 1行1要素のタプル
            param2 delimiter: 区切り文字 デフォルトは ";"
        Returns:
            tuple()
        """
        ret = tuple()
        tmp_lines = list()
        split_line = list()
        regexp_delimiter = ".*{}.+".format(SQL_DELIMITER_STATEMENT)
        if delimiter is None:
            delimiter = SQL_DELIMITER
        for line in lines:
            if self.is_matched(line=line, search_objs=[regexp_delimiter]):
                try:
                    split_line = line.split()
                    idx = split_line.index(SQL_DELIMITER_STATEMENT)
                except ValueError as e:
                    try:
                        idx = split_line.index(SQL_DELIMITER_STATEMENT.lower())
                    except:
                        print("区切り文字の捜索に失敗しました。捜索に失敗した行: "
                              .format(line))
                        raise
                except IndexError as index_e:
                    print("存在しない Index が指定されました。")
                    raise
                else:
                    delimiter = split_line[idx + 1]
            split_line = line.rstrip().split()
            tmp_lines.append(' '.join(split_line))
            if line[(len(line) - len(delimiter))::] == delimiter:
                ret += (' '.join(tmp_lines), )
                tmp_lines = list()
        return ret

    def is_utf8_with_bom(self, path: str):
        """文字コード UTF-8 のテキストファイルが BOM ありかどうかを判別する"""
        with codecs.open(path, mode="r", encoding="utf-8") as f:
            first_line = (f.readline()).rstrip()
            if first_line == "\ufeff":
                return True
            else:
                return False

    def is_matched(self, line: str, search_objs: list):
        """引数で渡されたパターンに基づいて文字列を捜索する.

        Args:
            param1 line: テキストファイル1行分にあたる文字列.
            param2 search_obj: 捜索パターンを正規表現で指定.

        Returns:
            パターンにマッチしたならTrue そうでないならFalseを返す.
        """
        if not isinstance(search_objs, list):
            search_objs = [search_objs]
        for search_obj in search_objs:
            match_obj = re.match(r'{}'.format(search_obj), line)
            if match_obj is not None:
                return True
            else:
                continue
        return False

    def join_lines(self, line: str, delimiter: str):
        """引数で渡された文字列を条件に基づいて処理をする.

        delimiterで指定された文字までを１行とみなす。

        AAAA
        BBBBBBB{delimiter}

        上の例では、AAAABBBBBBB;を１行として出力する.

        Args:
            param1 line: テキストファイル１行分にあたる文字列.
            param2 delimiter: 区切り文字とみなすリテラル

        Returns:
            1行とみなした文字列を返す.
        """
        self.list_str.append(line.rstrip().split())
        if not line.rstrip()[(len(line) - len(delimiter))::] == delimiter:
            return ''
        for list_element in self.list_str:
            self.with_combined += ' '.join(list_element) + ' '
        self.list_str = list()
        ret_str = self.with_combined
        self.with_combined = ''
        return ret_str.rstrip()

    def write_text_file(self, str_line: str, dir_path: str, mode: str, encode=None):
        """引数で受け取った文字列をファイルに書き込む.

        :param str_line: 書き込む文字列.
        :param dir_path: 出力ファイルのパス.
        :param mode: 書き込みモード
                     'w' = 上書きモード
                     'a' = 追記モード
        :param encode: 文字エンコーディングの指定 デフォルトはUTF-8.
        """
        if encode is None:
            encode = 'utf_8'
        try:
            with codecs.open(r'{}'.format(dir_path), mode=mode, encoding=encode) as file:
                file.write(str(str_line))
        except FileNotFoundError as e:
            print("\n存在しないファイルです。パス指定が正しいかどうか確認してください。\n")
            raise e
        except UnicodeError as e:
            print("\nエラー原因: " + e.reason)
            print("文字エンコーディングの指定を変更してみるといいかもしれない\n")
            raise e
        except (LookupError, ValueError) as e:
            print("存在しない、または無効な値です。")
            raise e
        else:
            pass

    def is_opened(self, dir_path: str, mode: str, encode=None):
        """
        ファイルがオープンできるかどうかの検査用メソッド.

        :param dir_path: ディレクトリパス.
        :param mode: オープンモード.
        :param encode: 文字エンコーディング.
        """
        if encode is None:
            encode = 'utf_8'
        try:
            with codecs.open(r'{}'.format(dir_path), mode=mode, encoding=encode) as file:
                for line in file:
                    pass
        except FileNotFoundError as e:
            print("\n存在しないファイルです。パス指定が正しいかどうか確認してください。\n")
            return False
        except UnicodeError as e:
            print("エラー発生\nエラー原因: " + e.reason)
            print("文字エンコーディングの指定を変更してみるといいかもしれない\n")
            return False
        except (LookupError, ValueError, OSError) as e:
            print("存在しない、または無効な値です。")
            return False
        else:
            if mode == 'w' or mode == 'a' and os.path.isfile(dir_path):
                os.remove(dir_path)
            return True


class ParseJSON(object):
    """class ParseJSON"""

    def __init__(self):
        """class ParseJSON Constructor

        Args:
            param1 path: json file path.
        """

    def load_json(self, file: str):
        """load json file.

        Args:
            param1 file: json file path.

        Returns:
            parsed object.(dict)

        Raises:
            FileNotFoundError
        """
        with open(file=file, mode='r') as f:
            dec_obj = json.loads(f.read())
            return dec_obj

    def out_json(self, file: str, content: str):
        """output the specified file in json format.

        Args:
            param1 file: output file path.(.json)
            param2 content: content of json file. it must be string data.

        Returns:
            file size of output file.

        Raises:
            FileNotFoundError
            json.JSONDecodeError(msg, doc, pos)
        """
        with open(file=file, mode="w") as f:
            return f.write(json.dumps(content, sort_keys=True, indent=4))
