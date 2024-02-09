import unittest
from dataclasses import dataclass
from typing import List, Union


class _ANSIColorCode:
    """
    ref: https://stackoverflow.com/a/287944
    """
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


@dataclass
class _TokenLine:
    is_ok: bool
    result: str
    info: Union[str, List[str]]
    

class BeautyTextResult(unittest.TextTestResult):
    COLORED = True

    def __init__(self, stream, descriptions: bool, verbosity: int):
        super().__init__(stream, descriptions, verbosity)
        self.stream = stream
        self.verbosity = verbosity
        self.descriptions = descriptions

        self.cached_tokens: List[_TokenLine] = []
        self.previous_testcase: Union[unittest.TestCase, None] = None

    def _get_test_info(self, test: unittest.TestCase) -> str:
        test_method = test._testMethodName
        module_name = test.__module__
        testcase_name = test.__class__.__qualname__
        info = f"{module_name}.{testcase_name}.{test_method}()"
        return info

    @staticmethod
    def _is_test_case_changed(prev_test: unittest.TestCase | None, curr_test: unittest.TestCase):
        if not prev_test:
            return True

        module_name = lambda test: test.__module__
        testcase_name = lambda test: test.__class__.__qualname__
        
        module_changed = module_name(prev_test) != module_name(curr_test)
        testcase_changed = testcase_name(prev_test) != testcase_name(curr_test)
        return module_changed or testcase_changed

    def _flush_cache(self):
        if len(self.cached_tokens) == 0:
            return
        
        get_result_token_len = lambda token_line: len(token_line.result)
        result_max_len = max([get_result_token_len(token_line) for token_line in self.cached_tokens])

        for token_line in self.cached_tokens:
            if self.COLORED:
                if token_line.is_ok:
                    status = _ANSIColorCode.OKGREEN + "O" + _ANSIColorCode.ENDC
                else:
                    status = _ANSIColorCode.FAIL + "X" + _ANSIColorCode.ENDC
            else:
                status = "O" if token_line.is_ok else "X"

            result = token_line.result
            if isinstance(token_line.info, list):
                info = " - ".join(token_line.info)
            else:
                info = token_line.info

            output_line = f"{status} - {result:{result_max_len}} ... {info}"
            self.stream.writeln(output_line)
        
        self.stream.flush()
        self.cached_tokens = []

    def _output_header(self, test: unittest.TestCase):
        module_name = test.__module__
        testcase_name = test.__class__.__qualname__
        self.stream.writeln(f"\n*** [{module_name}.{testcase_name}] ***")
        self.stream.flush()

    def startTest(self, test: unittest.TestCase):
        if self._is_test_case_changed(self.previous_testcase, test) and self.verbosity > 1:
            self._flush_cache()
            self._output_header(test)
        unittest.TestResult.startTest(self, test)
    
    def stopTest(self, test: unittest.TestCase):
        self.previous_testcase = test
        return super().stopTest(test)
    
    def stopTestRun(self) -> None:
        if self.verbosity > 1:
            self._flush_cache()
        return super().stopTestRun()

    def addSuccess(self, test: unittest.TestCase):
        if self.verbosity <= 1:
            super().addSuccess(test)
        else:
            info = self._get_test_info(test)
            self.cached_tokens.append(_TokenLine(True, "ok", info))
            unittest.TestResult.addSuccess(self, test)

    def addError(self, test: unittest.TestCase, err):
        if self.verbosity <= 1:
            super().addError(test, err)
        else:
            info = self._get_test_info(test)
            self.cached_tokens.append(_TokenLine(False, "EXCEPTION", info))
            unittest.TestResult.addError(self, test, err)

    def addFailure(self, test: unittest.TestCase, err):
        if self.verbosity <= 1:
            super().addFailure(test, err)
        else:
            info = self._get_test_info(test)
            self.cached_tokens.append(_TokenLine(False, "FAIL", info))
            unittest.TestResult.addFailure(self, test, err)

    def addSkip(self, test: unittest.TestCase, reason: str):
        if self.verbosity <= 1:
            super().addSkip(test, reason)
        else:
            info = self._get_test_info(test)
            if reason:
                info = [info, f"skip_reason = ({reason})"]
            self.cached_tokens.append(_TokenLine(True, "skipped", info))
            unittest.TestResult.addSkip(self, test, reason)

    def addExpectedFailure(self, test: unittest.TestCase, err):
        if self.verbosity <= 1:
            super().addExpectedFailure(test, err)
        else:
            info = self._get_test_info(test)
            self.cached_tokens.append(_TokenLine(True, "expected fail", info))
            unittest.TestResult.addExpectedFailure(self, test, err)

    def addUnexpectedSuccess(self, test: unittest.TestCase):
        if self.verbosity <= 1:
            super().addUnexpectedSuccess(test)
        else:
            info = self._get_test_info(test)
            self.cached_tokens.append(_TokenLine(False, "UNEXPECTED PASS", info))
            unittest.TestResult.addUnexpectedSuccess(self, test)