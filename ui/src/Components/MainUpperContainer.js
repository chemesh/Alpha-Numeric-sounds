import React from 'react'
import styled from 'styled-components'
import {ADVANCED_SETTINGS_TEXT} from '../constants/app_constants'
import InputSection from './InputArea/InputSection'
import SettingsArea from './SettingsArea/SettingsArea'
import SettingsButton from './SettingsArea/SettingsButton'
import PlayArea from './PlayArea/Components/PlayArea'

const MainUpperContainer = ({
    error,
    resetError,
    isReady,
    isShowSettings,
    doShowSettings,
    dontShowSettings,
}) => {
    const ErrorRow = () => {
        return error ? <ErrorArea>{error}</ErrorArea> : null
    }

    if (isReady) {
        return (
            <Container>
                <PlayArea />
            </Container>
        )
    }
    if (isShowSettings) {
        return (
            <Container>
                <SettingsArea save={() => dontShowSettings()} />
                <ErrorRow />
            </Container>
        )
    }
    return (
        <Container>
            <InputSection resetError={resetError} />
            <ErrorRow />
            <InnerContainer>
                <SettingsButton
                    onClick={doShowSettings}
                    text={ADVANCED_SETTINGS_TEXT}
                />
            </InnerContainer>
        </Container>
    )
}

export default MainUpperContainer

const Container = styled.div`
    display: flex-column;
    align-items: center;
    justify-content: center;
`
const InnerContainer = styled(Container)`
    display: flex;
`
const ErrorArea = styled.div`
    align-items: center;
    text-align: center;
    justify-content: center;
    color: black;
`
