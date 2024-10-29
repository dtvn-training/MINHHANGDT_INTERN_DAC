import unittest
import sys
import os
from nose2.tools import such

# Thêm đường dẫn đến thư mục gốc của project
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from logics import animal

with such.A('animal') as it:
    @it.has_setup
    def setup():
        # Khởi tạo đối tượng Dog cho tất cả các bài kiểm thử
        it.name = 'Mikey'
        it.age = 6
        it.instance = animal.Dog(it.name, it.age)

    @it.has_teardown
    def teardown():
        print('Teardown: Done.')
        return
        # os.remove('german_dog.txt')

    with it.having('Dog'):
        with it.having('description'):
            @it.should('Success write dog information to txt file')
            def test():
                # Sử dụng instance đã được tạo trong setup() từ it
                actual_result = it.instance.description()

                # Kiểm tra kết quả
                it.assertEqual(f"{it.name} is {it.age} years old", actual_result)

                output_file = 'german_dog.txt'
                with open(output_file, 'r') as f:
                    actual_infor = f.read()
                it.assertEqual(f"{it.name} is {it.age} years old", actual_infor)

        with it.having('speak'):
            @it.should('Success case. Return sound of Dog.')
            def test():
                # Sử dụng instance đã được tạo trong setup() từ it
                actual_result = it.instance.speak("Gruff Gruff")

                # Kiểm tra kết quả
                it.assertEqual(f"{it.name} says Gruff Gruff", actual_result)

    it.createTests(globals())

if __name__ == '__main__':
    unittest.main()
