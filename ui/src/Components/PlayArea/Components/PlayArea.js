import React, {useContext, useState} from 'react'
import styled from 'styled-components'
import PlayButton from './PlayButton'
import PingButton from '../PingButton'
import {InputContext} from '../../../App'
import {PROMPT_BY_REQUEST_STATUS} from '../../../constants/app_constants'
import {IMAGE_BY_STATUS} from '../../../utils/utils'
import axios from 'axios'
import {apiRoutes} from '../../../Api/routes'

const PlayArea = () => {
    const {trackingId, setRequestStatus, requestStatus} =
        useContext(InputContext)

    const [audioResult, setAudioResult] = useState(null)
    const [isPlay, setIsPlay] = useState(false)

    const imageToShow = IMAGE_BY_STATUS[requestStatus]
    const requestHeader = apiRoutes.pollUpdates + trackingId
    const canPlay =
        requestStatus === PROMPT_BY_REQUEST_STATUS.DONE && audioResult

    const pollUpdates = () => {
        axios.get(requestHeader).then((response) => {
            const status = response?.data?.status
            if (status) {
                setRequestStatus(status)
            }
            if (response.data?.isReady && response.data?.file64) {
                const song = response.data?.file64
                const audio = new Audio('data:audio/wav;base64,' + song)
                setAudioResult(audio)
            }
        })
    }

    const playResult = () => {
        !isPlay ? audioResult?.play() : audioResult?.pause()
        setIsPlay((prev) => !prev)
    }

    return (
        <Container>
            <InnerContainer>
                {!canPlay ? (
                    <PingButton onclick={pollUpdates}/>
                ) : (
                    <PlayButton onclick={playResult}
                                isPlay={isPlay}/>
                )}
            </InnerContainer>
            <StatusUpdate src={imageToShow}/>
        </Container>
    )
}

export default PlayArea

const Container = styled.div`
    align-items: center;
    justify-content: space-around;
`
const InnerContainer = styled.div`
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 10px;
`
const StatusUpdate = styled.img`
    height: 100px;
    margin-bottom: -20px;
`
