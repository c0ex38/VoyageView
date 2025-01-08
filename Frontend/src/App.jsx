import { BrowserRouter, Routes, Route } from 'react-router-dom'
import BaseLayout from './layouts/BaseLayout'
import AuthLayout from './layouts/AuthLayout'
import SmoothScroll from './components/SmoothScroll'
import Home from './pages/Home'
import Login from './pages/Login'
import Register from './pages/Register'
import VerifyEmail from './pages/VerifyEmail'
import Profile from './pages/Profile'
import EditProfile from './pages/EditProfile'
import { AuthProvider } from './context/AuthContext'
import CreatePost from './pages/CreatePost'
import Feed from './pages/Feed'
import { Toaster } from 'react-hot-toast'
import Popular from './pages/Popular'
import PostDetail from './pages/PostDetail'
import UserPosts from './pages/UserPosts'
import EditPost from './pages/EditPost'

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <SmoothScroll>
          <Routes>
            {/* Auth Routes - Footer ve ana navbar olmayan sayfalar */}
            <Route element={<AuthLayout />}>
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />
            </Route>

            {/* Main Routes - Footer ve ana navbar olan sayfalar */}
            <Route element={<BaseLayout />}>
              <Route index element={<Home />} />
              <Route path="/popular" element={<Popular />} />
            </Route>

            <Route path="verify-email" element={<VerifyEmail />} />
            <Route path="/profile/:username" element={<Profile />} />
            <Route path="/profile/settings" element={<EditProfile />} />
            <Route path="/create-post" element={<CreatePost />} />
            <Route path="/feed" element={<Feed />} />
            <Route path="/post/:id" element={<PostDetail />} />
            <Route path="/profile/:username/posts" element={<UserPosts />} />
            <Route path="/post/edit/:postId" element={<EditPost />} />
          </Routes>
        </SmoothScroll>
        <Toaster position="top-right" />
      </BrowserRouter>
    </AuthProvider>
  )
}

export default App
