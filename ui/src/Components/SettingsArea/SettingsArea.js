import React, {useContext, useState} from 'react'
import styled from 'styled-components'
import Colors from '../../constants/Colors'
import SettingInput from './SettingInput'
import {InputContext} from '../../App'
import SettingsButton from './SettingsButton'
import {
    DEFAULT_SETTINGS,
    SETTINGS_TITLE,
    GENERATIONS,
    POPULATION,
    MUTATION,
    CROSSOVER,
    SELECTION,
    SAVE_SETTINGS,
} from '../../constants/app_constants'

const SettingsArea = ({save}) => {
    const {setQueryOptions} = useContext(InputContext)
    const [generations, setGenerations] = useState(DEFAULT_SETTINGS.GENERATIONS)
    const [population, setPopulation] = useState(DEFAULT_SETTINGS.POPULATION)
    const [selection, setSelection] = useState(DEFAULT_SETTINGS.SELECTION)
    const [mutation, setMutation] = useState(DEFAULT_SETTINGS.MUTATION)
    const [crossover, setCrossover] = useState(DEFAULT_SETTINGS.CROSSOVER)

    const submit = () => {
        save()
        setQueryOptions({
            generations,
            population,
            selection,
            mutation,
            crossover,
        })
    }
    return (
        <Container>
            <Title>{SETTINGS_TITLE}</Title>
            <SettingInput
                setting={generations}
                setSetting={setGenerations}
                label={GENERATIONS}
            />
            <SettingInput
                setting={population}
                setSetting={setPopulation}
                label={POPULATION}
            />
            <SettingInput
                setting={selection}
                setSetting={setSelection}
                label={SELECTION}
            />
            <SettingInput
                setting={mutation}
                setSetting={setMutation}
                label={MUTATION}
            />
            <SettingInput
                setting={crossover}
                setSetting={setCrossover}
                label={CROSSOVER}
            />
            <BottomContainer>
                <SettingsButton
                    onClick={submit}
                    text={SAVE_SETTINGS}></SettingsButton>
            </BottomContainer>
        </Container>
    )
}

export default SettingsArea

const Container = styled.div`
    display: grid;
`
const Title = styled.div`
    color: ${Colors.TRANSPARENT_GREY};
    font-size: 26px;
    font-style: italic;
    margin-bottom: 20px;
    text-transform: capitalize;
`
const BottomContainer = styled.div`
    width: 100%;
    justify-content: center;
    display: flex;
    align-items: center;
`
