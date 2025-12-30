module.exports = {
  transpileDependencies: [
    '@thatopen/components',
    '@thatopen/fragments',
    'web-ifc'
  ],
  devServer: {
    client: {
      overlay: {
        runtimeErrors: (error) => {
          const msg = error.message || ''
          return !msg.includes('ResizeObserver loop completed with undelivered notifications')
        },
      },
    },
  },
  }
