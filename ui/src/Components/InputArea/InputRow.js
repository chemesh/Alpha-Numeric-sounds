import React, {useState} from 'react'
import styled from 'styled-components'
import {YOUTUBE_BASE_URL} from '../../constants/app_constants'
import YOUTUBE_ICON from '../../assets/youtube.png'
import PLUS from '../../assets/plus.png'
import READY from '../../assets/V.png'
import LinkInput from './LinkInput'
import {validateYoutubeLink} from '../../utils/utils'

const InputRow = ({url, setUrl, resetError}) => {
    const [link, setLink] = useState('')
    const [ready, setReady] = useState(false)

    const handleAddUrl = (e) => {
        e.preventDefault()
        resetError()
        if (validateYoutubeLink(link)) {
            setUrl(link)
            setReady(true)
        }
    }

    if (!ready)
        return (
            <LinkRow>
                <YouTubeLink href={YOUTUBE_BASE_URL} target="_blank">
                    <IconYT src={YOUTUBE_ICON}></IconYT>
                </YouTubeLink>
                <LinkInput
                    link={link}
                    savedUrl={url}
                    setLink={setLink}
                    submit={handleAddUrl}
                />
                <SubmitButton onClick={handleAddUrl}>
                    <PlusIcon src={PLUS} />
                </SubmitButton>
            </LinkRow>
        )
    return (
        <LinkRow>
            <YouTubeLink href={url ?? YOUTUBE_BASE_URL} target="_blank">
                <IconYT src={YOUTUBE_ICON} />
            </YouTubeLink>
            <LinkInput link={link} disabled />
            <SubmitButton>
                <ReadyIcon src={READY} />
            </SubmitButton>
        </LinkRow>
    )
}

export default InputRow

const LinkRow = styled.div`
    display: flex;
    align-items: center;
    justify-content: space-around;
    margin-top: 20px;
`
export const IconYT = styled.img`
    height: 70px;
    background: transparent;
`
const PlusIcon = styled(IconYT)``
const ReadyIcon = styled(IconYT)``
const SubmitButton = styled.button`
    border-radius: 20px;
    border-width: 0px;
    background: transparent;
    height: 50px;
    width: 50px;
    align-items: center;
    justify-content: center;
    display: flex;
`
const YouTubeLink = styled.a``
