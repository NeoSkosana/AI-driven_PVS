/// <reference types="@testing-library/jest-dom" />
import '@testing-library/jest-dom';

// Extend window with any custom properties
declare interface Window {
  // Add any custom window properties here
}

// React Query type augmentation
declare module '@tanstack/react-query' {
  interface Register {
    defaultError: Error;
  }
}

declare module '*.css' {
  const content: { [className: string]: string };
  export default content;
}

declare module '*.svg' {
  import * as React from 'react';

  export const ReactComponent: React.FunctionComponent<React.SVGProps<
    SVGSVGElement
  > & { title?: string }>;

  const src: string;
  export default src;
}

declare module '*.png' {
  const content: string;
  export default content;
}

declare module '*.jpg' {
  const content: string;
  export default content;
}

// Add any other module declarations as needed
