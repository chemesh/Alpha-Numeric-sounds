import DONE from '../assets/done.png'
import FETCH from '../assets/fetch.png'
import PRE from '../assets/gotrequest.png'
import MIX from '../assets/mix.png'
import ERROR from '../assets/error.png'
import {PROMPT_BY_REQUEST_STATUS} from '../constants/app_constants'

export const IMAGE_BY_STATUS = {
    [PROMPT_BY_REQUEST_STATUS.PRE]: PRE,
    [PROMPT_BY_REQUEST_STATUS.INIT]: FETCH,
    [PROMPT_BY_REQUEST_STATUS.IN_PROGRESS]: MIX,
    [PROMPT_BY_REQUEST_STATUS.DONE]: DONE,
    [PROMPT_BY_REQUEST_STATUS.ERROR]: ERROR,
}

const YOUTUBE_LINK_URL_CORE = 'youtu'

export const validateYoutubeLink = (url) => url && url.includes(YOUTUBE_LINK_URL_CORE)
