const ENV = 'dev'
const HOST = ENV === 'dev' ? 'http://127.0.0.1:8080' : 'later'

export const apiRoutes = {
    pollUpdates: `${HOST}/pollForUpdates/`,
    postSongs: `${HOST}/addSongsFromUrl`
}
