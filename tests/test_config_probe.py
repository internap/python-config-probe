import unittest

import os
from config_probe import probe, fake_probe
from config_probe.exceptions import ConfigNotFound
from hamcrest import is_, assert_that, has_key


class TestConfigProbe(unittest.TestCase):
    def test_single_file(self):
        config = probe(path=_dir("single-file"),
                       patterns=["stuff.yaml"])

        assert_that(config.key, is_("stuff-value"))
        assert_that(config.fruits, is_(["Apple", "Orange"]))

    def test_single_file_with_namespace(self):
        config = probe(path=_dir("single-file-with-namespace"),
                       patterns=["(*).json"])

        assert_that(config.stuff.key, is_("stuff-value"))

    def test_single_file_with_namespace_with_wrong_key(self):
        config = probe(path=_dir("single-file-with-namespace"),
                       patterns=["(*).json"])

        with self.assertRaises(ConfigNotFound):
            print(config.stuff.key_inexistant)

    def test_single_file_multiple_level_raising_or_not(self):
        config = probe(path=_dir("multi-level-files"),
                       patterns=["(*)/(*).yaml", "(*)/subdir/(*).yaml"])
        assert_that(config.ns1.stuff.we.need.more.cowbell, is_("ok"))

        with self.assertRaises(ConfigNotFound):
            print(config.ns1.stuff.we.need.less.cowbell)

    def test_two_files_with_subdir_namespace(self):
        config = probe(path=_dir("two-files-with-subdir-namespace"),
                       patterns=["(*)/(*).yaml"])

        assert_that(config.ns1.stuff.key1, is_("stuff from ns1"))
        assert_that(config.ns2.stuff.key2, is_("stuff from ns2"))

    def test_only_starred_parts_are_namespaced(self):
        config = probe(path=_dir("two-files-with-subdir-namespace"),
                       patterns=["(*)/stuff.yaml"])

        assert_that(config.ns1.key1, is_("stuff from ns1"))
        assert_that(config.ns2.key2, is_("stuff from ns2"))

    def test_using_only_a_star_does_not_count_toward_namespacing(self):
        config = probe(path=_dir("two-files-with-subdir-namespace"),
                       patterns=["*/stuff.yaml"])

        assert_that(config.key1, is_("stuff from ns1"))
        assert_that(config.key2, is_("stuff from ns2"))

    def test_multiple_patterns(self):
        config = probe(path=_dir("two-files-with-subdir-namespace"),
                       patterns=["ns1/(*).yaml", "(*)/stuff.yaml"])

        assert_that(config.stuff.key1, is_("stuff from ns1"))
        assert_that(config.ns2.key2, is_("stuff from ns2"))

    def test_multiple_patterns_on_same_namespaces_should_merge_recursively(self):
        config = probe(path=_dir("multi-level-files"),
                       patterns=["(*)/(*).yaml", "(*)/subdir/(*).yaml"])

        assert_that(config.ns1.stuff.content1.key1, is_("value1"))
        assert_that(config.ns1.stuff.content2.key2, is_("value2"))

    def test_pattern_order_defines_which_files_have_the_authority(self):
        config = probe(path=_dir("key-override"),
                       patterns=["file1.yaml", "file2.yaml"])
        assert_that(config.key, is_("value2"))

        config = probe(path=_dir("key-override"),
                       patterns=["file2.yaml", "file1.yaml"])
        assert_that(config.key, is_("value1"))

    def test_yaml_dict_are_merged_list_arent(self):
        config = probe(path=_dir("dict-merge"),
                       patterns=["file1.yaml", "file2.yaml"])
        assert_that(config.mydict.common_key, is_("value2"))
        assert_that(config.mydict.only_in_1, is_("value1"))
        assert_that(config.mydict.only_in_2, is_("value2"))
        assert_that(config.mydict.subdict.common_list, is_(["a2", "b2"]))
        assert_that(config.mydict.subdict.only_in_1, is_("value1"))
        assert_that(config.mydict.subdict.only_in_2, is_("value2"))

        config = probe(path=_dir("dict-merge"),
                       patterns=["file2.yaml", "file1.yaml"])
        assert_that(config.mydict.common_key, is_("value1"))
        assert_that(config.mydict.only_in_1, is_("value1"))
        assert_that(config.mydict.only_in_2, is_("value2"))
        assert_that(config.mydict.subdict.common_list, is_(["a1", "b1"]))
        assert_that(config.mydict.subdict.only_in_1, is_("value1"))
        assert_that(config.mydict.subdict.only_in_2, is_("value2"))

    def test_dict_should_behave_as_dict(self):
        config = probe(path=_dir("single-file"),
                       patterns=["(*).yaml"])

        assert_that(config["stuff"]["key"], is_("stuff-value"))
        assert_that(dict(config), has_key('stuff'))
        assert_that(dict(**config), has_key('stuff'))
        assert_that(dict(config.stuff), has_key('key'))
        assert_that(dict(**config.stuff), has_key('key'))

    def test_support_for_empty_files(self):
        probe(path=_dir("empty-files"), patterns=["*.*"])

    def test_support_absolute_paths_outside_base_dir(self):
        config = probe(path=_dir("single-file-with-namespace"), patterns=[
            "{}/(*)/(*)/stuff.yaml".format(os.path.dirname(__file__))
        ])
        assert_that(config['two-files-with-subdir-namespace'].ns1.key1, is_("stuff from ns1"))
        assert_that(config['two-files-with-subdir-namespace'].ns2.key2, is_("stuff from ns2"))

    def test_fake_probe(self):
        config = fake_probe({
            "key": "value",
            "key2": [
                {"hey": "ho"}
            ]
        })

        assert_that(config.key, is_("value"))
        assert_that(config.key2[0].hey, is_("ho"))

        with self.assertRaises(ConfigNotFound):
            print(config.unknown)


def _dir(name):
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), name)
