# Copyright 2015-2021 Mathieu Bernard
#
# This file is part of phonemizer: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# Phonemizer is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with phonemizer. If not, see <http://www.gnu.org/licenses/>.
"""Test of the espeak backend language switch processing"""

# pylint: disable=missing-docstring
# pylint: disable=redefined-outer-name

import pytest

from phonemizer.backend import EspeakBackend
from phonemizer.separator import Separator


@pytest.fixture
def langswitch_text():
    return [
        "j'aime l'anglais",
        "j'aime le football",
        "football",
        "surtout le real madrid",
        "n'utilise pas google"]


@pytest.mark.skipif(
    not EspeakBackend.is_espeak_ng(),
    reason='language switch only exists for espeak-ng')
@pytest.mark.parametrize('njobs', [1, 3])
def test_language_switch_keep_flags(caplog, langswitch_text, njobs):
    backend = EspeakBackend('fr-fr', language_switch='keep-flags')
    out = backend.phonemize(
        langswitch_text, separator=Separator(), strip=True, njobs=njobs)
    assert out == [
        'ʒɛm lɑ̃ɡlɛ',
        'ʒɛm lə (en)fʊtbɔːl(fr)',
        '(en)fʊtbɔːl(fr)',
        'syʁtu lə (en)ɹiəl(fr) madʁid',
        'nytiliz pa (en)ɡuːɡəl(fr)']

    messages = [msg[2] for msg in caplog.record_tuples]
    assert (
        '4 utterances containing language switches on lines 2, 3, 4, 5'
        in messages)
    assert (
        'language switch flags have been kept (applying "keep-flags" policy)'
        in messages)


@pytest.mark.skipif(
    not EspeakBackend.is_espeak_ng(),
    reason='language switch only exists for espeak-ng')
@pytest.mark.parametrize('njobs', [1, 3])
def test_language_switch_default(caplog, langswitch_text, njobs):
    # default behavior is to keep the flags
    backend = EspeakBackend('fr-fr')
    out = backend.phonemize(
        langswitch_text, separator=Separator(), strip=True, njobs=njobs)
    assert out == [
        'ʒɛm lɑ̃ɡlɛ',
        'ʒɛm lə (en)fʊtbɔːl(fr)',
        '(en)fʊtbɔːl(fr)',
        'syʁtu lə (en)ɹiəl(fr) madʁid',
        'nytiliz pa (en)ɡuːɡəl(fr)']

    messages = [msg[2] for msg in caplog.record_tuples]
    assert (
        '4 utterances containing language switches on lines 2, 3, 4, 5'
        in messages)
    assert (
        'language switch flags have been kept (applying "keep-flags" policy)'
        in messages)


@pytest.mark.skipif(
    not EspeakBackend.is_espeak_ng(),
    reason='language switch only exists for espeak-ng')
@pytest.mark.parametrize('njobs', [1, 3])
def test_language_switch_remove_flags(caplog, langswitch_text, njobs):
    backend = EspeakBackend('fr-fr', language_switch='remove-flags')
    out = backend.phonemize(
        langswitch_text, separator=Separator(), strip=True, njobs=njobs)
    assert out == [
        'ʒɛm lɑ̃ɡlɛ',
        'ʒɛm lə fʊtbɔːl',
        'fʊtbɔːl',
        'syʁtu lə ɹiəl madʁid',
        'nytiliz pa ɡuːɡəl']

    messages = [msg[2] for msg in caplog.record_tuples]
    assert (
        '4 utterances containing language switches on lines 2, 3, 4, 5'
        in messages)
    assert (
        'language switch flags have been removed '
        '(applying "remove-flags" policy)'
        in messages)


@pytest.mark.skipif(
    not EspeakBackend.is_espeak_ng(),
    reason='language switch only exists for espeak-ng')
@pytest.mark.parametrize('njobs', [1, 3])
def test_language_switch_remove_utterance(caplog, langswitch_text, njobs):
    backend = EspeakBackend('fr-fr', language_switch='remove-utterance')
    out = backend.phonemize(
        langswitch_text, separator=Separator(), strip=True, njobs=njobs)
    assert out == ['ʒɛm lɑ̃ɡlɛ', '', '', '', '']

    messages = [msg[2] for msg in caplog.record_tuples]
    assert (
        'removed 4 utterances containing language switches '
        '(applying "remove-utterance" policy)'
        in messages)

    with pytest.raises(RuntimeError):
        backend = EspeakBackend('fr-fr', language_switch='foo')


@pytest.mark.skipif(
    not EspeakBackend.is_espeak_ng(),
    reason='language switch only exists for espeak-ng')
@pytest.mark.parametrize(
    'policy', ('keep-flags', 'remove-flags', 'remove-utterance'))
def test_no_switch(policy, caplog):
    text = ["j'aime l'anglais", "tu parles le français"]
    backend = EspeakBackend('fr-fr', language_switch=policy)
    out = backend.phonemize(text, separator=Separator(), strip=True)
    assert out == ['ʒɛm lɑ̃ɡlɛ', 'ty paʁl lə fʁɑ̃sɛ']

    messages = [msg[2] for msg in caplog.record_tuples]
    assert not messages
