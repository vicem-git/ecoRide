import ReactDOM from 'react-dom/client'
import { StrictMode, Suspense, lazy } from 'react'
import { createBrowserRouter, RouterProvider } from 'react-router'
import './index.css'
import App from './App.tsx'


const SearchPage = lazy(() => import('./pages/SearchPage.tsx'))
const CreateTripPage = lazy(() => import('./pages/CreateTripPage.tsx'))
const SignupPage = lazy(() => import('./pages/SignupPage.tsx'))
const LoginPage = lazy(() => import('./pages/LoginPage.tsx'))

const router = createBrowserRouter([
  {
    path: '/',
    element: <App />,
  },
  {
    path: '/signup',
    element: (
      <Suspense fallback={<div>Loading...</div>}>
        <SignupPage />
      </Suspense>
    ),
  },
  {
    path: '/login',
    element: (
      <Suspense fallback={<div>Loading...</div>}>
        <LoginPage />
      </Suspense>
    ),
  },
  {
    path: '/search',
    element: (
      <Suspense fallback={<div>Loading...</div>}>
        <SearchPage />
      </Suspense>
    ),
  },
  {
    path: '/create-trip',
    element: (
      <Suspense fallback={<div>Loading...</div>}>
        <CreateTripPage />
      </Suspense>
    ),
  },
]);

const root = document.getElementById('root');

ReactDOM.createRoot(root!).render(
  <StrictMode>
    <RouterProvider router={router} />
  </StrictMode>
);
