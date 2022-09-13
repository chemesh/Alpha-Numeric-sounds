import React from 'react'
import styled from 'styled-components'
import PING from '../../assets/ping.png'

const PingButton = ({onclick}) => {
    return (
        <Container onClick={onclick}>
            <Icon src={PING} />
        </Container>
    )
}

export default PingButton

const Container = styled.button`
    border-radius: 20px;
    border-width: 0px;
    background: transparent;
    align-items: center;
    justify-content: center;
`
const Icon = styled.img`
    height: 100px;
`
