/// <reference types="vite/client" />

declare module '*.vue' {
  import type { DefineComponent } from 'vue'
  const component: DefineComponent<Record<string, unknown>, Record<string, unknown>, any>
  export default component
}

interface ImportMetaEnv {
  readonly VITE_APP_TITLE: string
  // 더 많은 환경 변수 타입을 여기에 추가할 수 있습니다
}

interface ImportMeta {
  readonly env: ImportMetaEnv
} 