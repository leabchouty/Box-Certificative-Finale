// Form.test.js
import { mount, flushPromises } from '@vue/test-utils'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { nextTick } from 'vue'

// Mocking Supabase for open form tests
vi.mock('../src/supabase', () => ({
  supabase: {
    auth: {
      getUser: vi.fn().mockResolvedValue({
        data: { user: { id: 'user123' } },
      }),
    },
    from: vi.fn((tableName) => {
      if (tableName === 'students') {
        return {
          select: vi.fn().mockReturnThis(),
          eq: vi.fn().mockReturnThis(),
          then: undefined,
          data: [
            { id: '1', name: 'Alice' },
            { id: '2', name: 'Bob' },
          ],
        }
      }
      if (tableName === 'settings') {
        return {
          select: vi.fn().mockReturnThis(),
          single: vi.fn().mockResolvedValue({
            data: {
              date: new Date(Date.now() + 100000), // future date
              isopen: true,
            },
          }),
        }
      }
      return {
        select: vi.fn().mockReturnThis(),
        single: vi.fn().mockResolvedValue({ data: {} }),
      }
    }),
  },
}))

import Form from '../src/views/Form.vue'

describe('Form.vue (Open)', () => {
  it('displays the form if isOpen is true and not locked', async () => {
    const wrapper = mount(Form)
    await flushPromises()
    expect(wrapper.text().toLowerCase()).toContain('assign points')
    expect(wrapper.find('form').exists()).toBe(true)
  })

  it('adds a new row when the last field is valid and total < 100', async () => {
    const wrapper = mount(Form)
    await flushPromises()

    const select = wrapper.find('select')
    expect(select.exists()).toBe(true)
    await select.setValue('Alice')

    const input = wrapper.find('input[type="number"]')
    expect(input.exists()).toBe(true)
    await input.setValue(30)
    await input.trigger('input')
    await nextTick()

    expect(wrapper.vm.fields.length).toBeGreaterThan(1)
  })

  it('disables submit button if total points is not 100', async () => {
    const wrapper = mount(Form)
    await flushPromises()

    const button = wrapper.find('button[type="submit"]')
    expect(button.exists()).toBe(true)
    expect(button.attributes('disabled')).toBeDefined()
  })
})
