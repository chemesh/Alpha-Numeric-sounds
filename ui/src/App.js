import React, {createContext, useState} from 'react'
import styled from 'styled-components'
import Colors from './constants/Colors'
import MainBottomContainer from './Components/MainBottomContainer'
import MainUpperContainer from './Components/MainUpperContainer'
import axios from 'axios'
import {apiRoutes} from './Api/routes'
import LOGO from './assets/logo_medium.png'
import DESCRIPTION from './assets/description.png'
import WAVEFORM from './assets/waveform.png'
import {DEFAULT_SETTINGS, ERROR_PROMPT, PROMPT_BY_REQUEST_STATUS,} from './constants/app_constants'

export const InputContext = createContext()

const App = () => {
    const [firstUrl, setFirstUrl] = useState(null)
    const [secondUrl, setSecondUrl] = useState(null)
    const [error, setError] = useState(null)
    const [ready, setReady] = useState(false)
    const [move, setMove] = useState(false)
    const [queryOptions, setQueryOptions] = useState(DEFAULT_SETTINGS)
    const [showAdvancedSettings, setShowAdvancedSettings] = useState(false)
    const [trackingId, setTrackingId] = useState(null)
    const [requestStatus, setRequestStatus] = useState(
        PROMPT_BY_REQUEST_STATUS.PRE,
    )

    const didInsertLinks = firstUrl && secondUrl
    const audioPrepared = requestStatus === PROMPT_BY_REQUEST_STATUS.DONE

    const postSongs = () => {
        axios
            .post(apiRoutes.postSongs, {
                urls: [firstUrl, secondUrl],
                advanced: queryOptions,
            })
            .then((response) => {
                console.log('got response from post', response.data)
                const {id: requestId, msg: status} = response?.data
                setTrackingId(requestId)
            })
    }

    const go = () => {
        if (didInsertLinks) {
            setMove(true)
            setReady(true)
            postSongs()
            if (error) {
                resetError()
            }
        } else {
            setError(ERROR_PROMPT)
        }
    }
    const resetError = () => {
        setError(null)
    }

    const doShowSettings = () => {
        resetError()
        setShowAdvancedSettings(true)
    }
    const dontShowSettings = () => {
        resetError()
        setShowAdvancedSettings(false)
    }

    return (
        <Container>
            {showAdvancedSettings && (
                <DescriptionPng src={DESCRIPTION}/>
            )}
            <Page>
                <Logo src={LOGO} />
                <InputContext.Provider
                    value={{
                        firstUrl,
                        setFirstUrl,
                        secondUrl,
                        setSecondUrl,
                        queryOptions,
                        setQueryOptions,
                        requestStatus,
                        setRequestStatus,
                        trackingId,
                    }}>
                    <MainUpperContainer
                        error={error}
                        resetError={resetError}
                        isReady={ready}
                        isShowSettings={showAdvancedSettings}
                        doShowSettings={doShowSettings}
                        dontShowSettings={dontShowSettings}
                    />
                </InputContext.Provider>
                <WaveForm src={WAVEFORM} move={move} ready={audioPrepared} />
                <MainBottomContainer
                    onClick={go}
                    isReady={ready}
                    audioPrepared={audioPrepared}
                    isShowSettings={showAdvancedSettings}
                />
            </Page>
        </Container>
    )
}

export default App

const Container = styled.div`
    width: 100vw;
    height: 100%;
    justify-content: space-around;
    align-items: center;
    align-content: center;
    background-color: #fffdd0;
    display: flex;
`
const Page = styled.div`
    display: flex;
    align-self: center;
    flex-direction: column;
    background-color: ${Colors.BLUE_NEW_BACKGROUND};
    padding: 2px;
    width: 40%;
    border-radius: 100px;
    align-items: center;
    justify-content: flex-start;
`
const Logo = styled.img`
    margin-top: 50px;
    // background: ${Colors.LIGHT_PURPLE_NEW};
`

const WaveForm = styled.img`
    height: 140px;
    width: 38vw;
    margin-top: 10px;
    margin-bottom: 10px;
    transform: rotate(0deg);
    transition: transform 100s ease-out;
    ${(props) =>
        props.move &&
        `
            transform: rotate(7200deg);
        `};
    ${(props) =>
        props.ready &&
        `
            transform: scale(2, 0.5);
        `};
`
const DescriptionPng = styled.img`
    justify-content: flex-start;
    max-width: 35%;
`
