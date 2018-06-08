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
        # 連結用文字列を格納しておく.
        joined_strs = ''
        joined_str = tuple()
        try:
            with codecs.open(dir_path, mode='r', encoding=encode) as file:
                for line in file:
                    if line in {'\n', '\r', '\r\n' }:
                        continue
                    elif self.is_matched(line=line.rstrip(), search_objs=["^-+", "^#+"]):
                        continue
                    elif self.is_matched(line=line.rstrip(), search_objs=["^(/\*).*(\*/)$"]):
                        continue
                    elif self.is_matched(line=line.rstrip(), search_objs=["^/\*"]) \
                        and comment_flag == False:
                        comment_flag = True
                        continue
                    elif self.is_matched(line=line.rstrip(), search_objs=["\*/$"]) \
                        and comment_flag == True:
                        comment_flag = False
                        continue
                    elif comment_flag == True:
                        continue
                    else:
                        joined_strs = self.join_lines(line)
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

    def is_matched(self, line: str, search_objs: list):
        """引数で渡されたパターンに基づいて文字列を捜索する.

        Args:
            param1 line: テキストファイル1行分にあたる文字列.
            param2 search_obj: 捜索パターン. 正規表現可.

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

    def join_lines(self, line: str):
        """引数で渡された文字列を条件に基づいて処理をする.

        セミコロンまでを１行とみなす。
        行の終端がセミコロンの行までを１行に連結する。

        AAAA
        BBBBBBB;

        上の例では、AAAABBBBBBB;を１行として出力する.

        Args:
            param1 line: テキストファイル１行分にあたる文字列.

        Returns:
            1行とみなした文字列を返す.
        """
        self.list_str.append(line.rstrip().split())
        if not line.rstrip()[-1] == ';':
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
