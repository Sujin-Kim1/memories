import React, { useState } from 'react'
import { Route, Switch } from 'react-router-dom'
import { ApolloProvider } from '@apollo/react-hooks'
import { ApolloClient } from 'apollo-client'
import { InMemoryCache } from 'apollo-cache-inmemory'
import { createUploadLink } from 'apollo-upload-client'
import MediaListPage from './pages/media-list-page'
import MediaViewPage from './pages/media-view-page'
import Header from './components/Header/header'
import UploadPage from './pages/upload-page'
import HomePage from './pages/home-page'
import LoginPage from './pages/login-page'
import RegisterPage from './pages/register-page'
import 'antd/dist/antd.css'

const URI = 'http://203.246.113.62:4000/'

function App () {
  const client = new ApolloClient({
    link: createUploadLink({ uri: URI }),
    cache: new InMemoryCache(),
  })
  const [token, setToken] = useState("")
  const getToken = (token) => {
    setToken(token)
  }
  return (
    <ApolloProvider client={client}>
      <Header token={token}/>
      <Switch>
        <Route exact path="/" component={HomePage}/>
        <Route exact path="/search" component={MediaListPage}/>
        <Route exact path="/watch" component={MediaViewPage}/>
        <Route exact path="/upload" component={UploadPage}/>
        <Route exact path="/login" render={()=> <LoginPage getToken={getToken}/>}/>
        <Route exact path="/register" component={RegisterPage}/>
      </Switch>
    </ApolloProvider>
  )
}

export default App
