// shims-vue.d.ts
// Declare module for .vue files so TypeScript recognizes Vue single-file component imports
declare module '*.vue' {
  import { DefineComponent } from 'vue'
  const component: DefineComponent<{}, {}, any>
  export default component
}
