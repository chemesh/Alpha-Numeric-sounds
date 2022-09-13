
# import server.Source.utils.Constants as consts
# import librosa
# import librosa.display
# import soundfile as sf
# # from spleeter.separator import Separator
# #
# # from Source.utils.Constants import WAV_FILE_TEST, INPUT_FOLDER
# from EA_Engine import EA_Engine
# import server.Source.utils.SoundUtils as su

from server.Source.utils.DataModels import Song
# from app.integrations.youtube_manager import YTManager
from server.Source.utils.Raters import sub_rater_verify_parts_length


LEVAD_BAMIDBAR = "C:\\Users\\roi.shemesh\\PycharmProjects\\Alpha-Numeric-sounds\\server\\resources\\לבד במדבר  -  גיא מזיג.wav"
SMOOTH = "C:\\Users\\roi.shemesh\\PycharmProjects\\Alpha-Numeric-sounds\\server\\resources\\Santana - Smooth ft. Rob Thomas (Official Video).wav"


def main():

    guy_mezig = Song.from_wav_file(LEVAD_BAMIDBAR)
    # santana = Song.from_wav_file(SMOOTH)
    print(f"santana bkps: {guy_mezig.segments_time_bkps}")
    # bkps = [62310.89381928583,53891.03382913407,43295.85459289886,33121.05721054307,26612.108632268006,16436.902588127294,13257.197343100666,10985.7665592448,9912.59527253611,9417.75031291199,9134.765719466373,8893.706686450334,8655.934685390048,8497.250757713968,8324.65803206701,8145.590992465207,7986.9070647891285]
    res = sub_rater_verify_parts_length(guy_mezig.segments_time_bkps)
    print(f"guy mezig's score: {res}")



    # urls = ['https://www.youtube.com/watch?v=CxKWTzr-k6s']
    # yt_manager = YTManager()
    # songs_paths = yt_manager.download(urls)
    # print(songs_paths)
    # # logger = Logger()
    # engine = EA_Engine()
    # s1 = s2 = Song(*songs_paths)
    # res = engine.mix(s1, s2)
    # print(res)

    # sep = Separator("spleeter:5stems")

    # data, samplerate = librosa.load(librosa.ex('trumpet'))
    # data, samplerate = librosa.load(librosa.ex('nutcracker'))
    # song1 = Song(WAV_FILE_TEST)
    # y1, sr1 = librosa.load(os.path.join(INPUT_FOLDER, "bohemian_raphsody.wav"), offset=30., duration=30)
    # y1, sr1 = librosa.load(WAV_FILE_TEST, duration=30)
    # y1, sr1 = librosa.load(f'{consts.INPUT_FOLDER}/lovestory.wav', duration=60)
    log = logger.Logger()
    y1, sr1 = librosa.load('C:\\Users\\roi.shemesh\\PycharmProjects\\Alpha-Numeric-sounds\\resources\\לבד במדבר  -  גיא מזיג.wav', duration=187)
    y1 = librosa.effects.trim(y1)
    timed_segs, bkps = su.break_to_timed_segments(y1, sr1, n_bkps_max=20)
    print(f'BKPS ------ {bkps}')
    print('segments ', timed_segs.shape)
    i = 0
    for seg in timed_segs:
        log.info(f'beginning of iter: seg.shape = {seg.shape}')
        bpm, beat_track = librosa.beat.beat_track(seg, sr1)
        seg_layers = su.separate_voices(seg)
        vocal_notes, _ = su.extract_notes(seg_layers[INSTRUMENT.VOCALS.value], beat_track)
        piano_notes, _ = su.extract_notes(seg_layers[INSTRUMENT.PIANO.value], beat_track)
        rate1 = (rate.sub_rater_neighboring_pitch(vocal_notes) + rate.sub_rater_neighboring_pitch(piano_notes))/2
        vocals_key = su.extract_key(seg_layers[INSTRUMENT.VOCALS.value], sr1)
        rate2 = rate.sub_rater_notes_in_key(vocal_notes, vocals_key)
        log.info(f'avg rate of iteration: {(rate1+rate2)/2}')
        #sf.write(f"{consts.INPUT_FOLDER}/love-{i}-vocals.wav", seg_layers[INSTRUMENT.VOCALS.value], sr1)
        #sf.write(f"{consts.INPUT_FOLDER}/love-{i}-piano.wav", seg_layers[INSTRUMENT.PIANO.value], sr1)
        log.info('========================================= FINISHED ITER =============================================')
        i += 1





    # tempo, beat_track = librosa.beat.beat_track(timed_segs[1], sr1)
    # key = su.extract_key(y1, sr1)
    # log.info(f'found key: {key}')
    # print('segments ', timed_segs.shape)
    # log.info('trying to extract frequencies for chords...')
    # layers_of_2nd_seg = su.separate_voices(timed_segs[1])
    # print(f'extract voices return {layers_of_2nd_seg.keys()}')
    # #layers_of_2nd_seg = su.slice_to_audio_layers(timed_segs[2], sr1)
    # notes, n_fft = su.extract_notes(layers_of_2nd_seg[INSTRUMENT.VOCALS.value], beat_track)
    # key = su.extract_key(layers_of_2nd_seg[INSTRUMENT.VOCALS.value], sr1)
    # log.info(f'key found is: {key}')
    # rms = librosa.feature.rms(layers_of_2nd_seg[INSTRUMENT.VOCALS.value], frame_length=n_fft)
    # log.info(f'rms found: {rms}, with shape {rms.shape}')
    # #notes = [list(map(su.to_mingus_form, notes)) for note in notes if type(note) != str and note is not None]
    # first_rate = rate.sub_rater_neighboring_pitch(notes)
    # log.info(f'neighboring pitch rating of vocals of second segment: {first_rate}')
    # second_rate = rate.sub_rater_notes_in_key(notes, key)
    # log.info(f'num of notes in key rating of vocals of second segment: {second_rate}')
    # sf.write(f"{consts.INPUT_FOLDER}/guess_who_mono.wav", layers_of_2nd_seg[0][0], sr1)

    # bkps = su.partition(y1, sr1, 10)
    # print(f"bkps: {bkps}")
    #y2, sr2 = librosa.load(os.path.join(INPUT_FOLDER, "im_rak_tedabri.wav"), duration=30)
    #
    # clean_y = su.get_clean_freq(y1)
    # sf.write(f"{consts.INPUT_FOLDER}/im_rak_tedabri.wav", y1, sr1)







    # song1 = Song(WAV_FILE_TEST)
    # song1 = Song(WAV_FILE_TEST, duration=60.0)
    # song2 = Song(librosa.ex('nutcracker'))
    # song3 = Song(librosa.ex('trumpet'))
    # mp3_to_wav(str(Path(INPUT_FOLDER)/"In-the-hall-of-the-mountain-king.mp3"))
    # wav_file = str(Path(INPUT_FOLDER)/"In-the-hall-of-the-mountain-king.wav")
    # data, samplerate = librosa.load(wav_file)
    # song2 = su.ndarr_to_as(song2.data)
    # song3 = su.ndarr_to_as(song3.data)

    # combined_data,  sr = su.combine(song2.data, song2.sr, song3.data, song3.sr)

    # sw1, sw2 = su.swap(song1.data, song1.sr, song2.data, song2.sr, 5, 10, 6.5, 9)
    #
    # # sf.write(f"{INPUT_FOLDER}/combined.wav", combined_data, sr)
    # sf.write(f"{INPUT_FOLDER}/sw1.wav", sw1, song1.sr)
    # sf.write(f"{INPUT_FOLDER}/sw2.wav", sw2, song2.sr)

    # sf.write(f"{INPUT_FOLDER}/rnd.wav", su.rand_reconstruct(y1, sr1, y2, sr2), sr1)


    # results = engine.mix(song1, song2)

    # from spleeter.audio.adapter import AudioAdapter

    # audio_loader = AudioAdapter.default()
    # waveform, sr = audio_loader.load(WAV_FILE_TEST, sample_rate=22050)

    # logger.info(f"data: {song1.data}, sample rate: {song1.sr}")
    # logger.info(f"type: {waveform.dtype}")
    # logger.info(f"size: {len(waveform)}")

    # song3.combine(song2)
    # sf.write(f"{INPUT_FOLDER}/song3.wav", song3.data, song3.sr)

    # song3_parts = sep.separate(song1.data.reshape(song1.data.shape[0],1))
    # for inst, data in song1_parts.items():
    #     logger.info(f"instrument: {inst}, data:{data}")
    #     sf.write(f"{INPUT_FOLDER}/{inst}.wav", data, song1.sr)

    # hop_length = 512
    # h_data, p_data = librosa.effects.hpss(song1.data)
    # logger.debug(f"decomposition values - \nHarmonic data: {h_data}\n Percussive data: {p_data}")
    #
    # tempo, beat_frames = librosa.beat.beat_track(y=p_data, sr=song1.sr)
    # logger.warn(f"tempo: {tempo:.2f}")
    #
    # beat_times = librosa.frames_to_time(beat_frames, sr=song1.sr)
    # logger.error(f"beat times: {beat_times}")
    #
    # # segments = partition(data, samplerate)
    #
    # # segment_freq = [librosa.stft(part) for part in segments]
    #
    # freq = librosa.stft(song1.data)
    # print(f"freq: {freq}")
    # mag, phase = librosa.magphase(freq)
    # print(f"mag: {mag}")
    # print(f"phase: {phase}")
    #
    # S_filter = librosa.decompose.nn_filter(mag,
    #                                        aggregate=np.median,
    #                                        metric='cosine',
    #                                        width=int(librosa.time_to_frames(2, sr=song1.sr)))
    #
    # # The output of the filter shouldn't be greater than the input
    # # if we assume signals are additive.  Taking the pointwise minimum
    # # with the input spectrum forces this.
    # S_filter = np.minimum(mag, S_filter)
    #
    # # We can also use a margin to reduce bleed between the vocals and instrumentation masks.
    # # Note: the margins need not be equal for foreground and background separation
    # margin_i, margin_v = 1, 10
    # power = 2
    #
    # mask_i = librosa.util.softmask(S_filter,
    #                                margin_i * (mag - S_filter),
    #                                power=power)
    #
    # mask_v = librosa.util.softmask(mag - S_filter,
    #                                margin_v * S_filter,
    #                                power=power)
    #
    # mask_back = librosa.util.softmask(S_filter,
    #                                   mag - S_filter,
    #                                   power=power)
    #
    # mask_lead = librosa.util.softmask(mag - S_filter,
    #                                   S_filter,
    #                                   power=power)
    #
    # # Once we have the masks, simply multiply them with the input spectrum
    # # to separate the components
    #
    # S_foreground = mask_v * mag
    # S_background = mask_back * mag
    #
    # fig, ax = plt.subplots(nrows=3, sharex=True, sharey=True)
    # img = librosa.display.specshow(librosa.amplitude_to_db(mag, ref=np.max),
    #                                y_axis='log', x_axis='time', sr=song1.sr, ax=ax[0])
    # ax[0].set(title='Full spectrum')
    # ax[0].label_outer()
    #
    # librosa.display.specshow(librosa.amplitude_to_db(S_background, ref=np.max),
    #                          y_axis='log', x_axis='time', sr=song1.sr, ax=ax[1])
    # ax[1].set(title='Background')
    # ax[1].label_outer()
    #
    # librosa.display.specshow(librosa.amplitude_to_db(S_foreground, ref=np.max),
    #                          y_axis='log', x_axis='time', sr=song1.sr, ax=ax[2])
    # ax[2].set(title='Foreground')
    # fig.colorbar(img, ax=ax)
    # fig.show()
    #
    # foreground = librosa.istft(S_foreground * phase)
    # background = librosa.istft(S_background * phase)
    #
    # sf.write(f"{INPUT_FOLDER}/foreground.wav", foreground, song1.sr)
    # sf.write(f"{INPUT_FOLDER}/background.wav", background, song1.sr)
    #
    # # notes = librosa.hz_to_note(freq)
    # # logger.info(f"notes: {notes[:5][:5]}")


if __name__ == "__main__":
    main()
