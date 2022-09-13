import React from 'react'
import styled from 'styled-components'
import PLUS from '../../assets/plus.png'
import {IconYT} from './InputRow'

const SubmitButton = ({onclick}) => {
    return (
        <Container>
            <PlusIcon onclick={onclick} src={PLUS} />
        </Container>
    )
}

export default SubmitButton

const Container = styled.button`
    border-radius: 20px;
    border-width: 0px;
    background: transparent;
    height: 50px;
    width: 50px;
    align-items: center;
    justify-content: center;
    display: flex;
`
const PlusIcon = styled(IconYT)`
    height: 50px;
    border-radius: 50px;
`
