const ENV = 'prod'
const HOST = ENV === 'dev' ? 'http://0.0.0.0:8080' : 'later'

export const apiRoutes = {
    pollUpdates: `${HOST}/pollForUpdates/`,
    postSongs: `${HOST}/addSongsFromUrl`
}
