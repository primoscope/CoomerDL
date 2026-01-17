import React from 'react'
import InputPanel from '@/components/InputPanel'
import ProgressPanel from '@/components/ProgressPanel'
import LogPanel from '@/components/LogPanel'

const HomePage: React.FC = () => {
  return (
    <>
      <InputPanel />
      <ProgressPanel />
      <LogPanel />
    </>
  )
}

export default HomePage
