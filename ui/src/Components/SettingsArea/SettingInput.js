import React from 'react'
import styled from 'styled-components'
import Colors from '../../constants/Colors'

const SettingInput = ({setting, setSetting, label}) => {
    return (
        <Form onSubmit={(e) => e.preventDefault()}>
            <Row>
                <Label>{label}</Label>
                <Input
                    onChange={(e) => setSetting(e.target.value)}
                    type="number"
                    value={setting}
                    placeholder={setting}
                />
            </Row>
        </Form>
    )
}

export default SettingInput

const Input = styled.input`
    display: flex;
    margin: 10px;
    width: 60px;
    height: 40px;
    border-radius: 20px;
    border-width: 3px;
    background: ${Colors.LIGHT_GREY};
    border-color: ${Colors.YELLOW};
    align-items: center;
    justify-content: center;
    text-align: center;
    color: black;
    font-size: 18px;
`
const Form = styled.form``
const Label = styled.label`
    font-style: italic;
    margin-right: 10px;
`
const Row = styled.span`
    display: flex;
    align-items: center;
    justify-content: space-between;
    text-align: center;
    font-size: 24px;
    color: ${Colors.BLUE};
`
