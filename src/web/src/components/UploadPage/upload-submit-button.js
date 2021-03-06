import React from 'react';
import { Button, Form } from 'antd';

const tailLayout = {
  wrapperCol: { offset: 4, span: 16 },
};

function UploadSubmitButton (props) {
  return (
    <Form.Item {...tailLayout}>
      {
        (props.isSubmit) ?
          <Button
            type="primary"
            size="large"
            onClick={props.onClick}
            htmlType="submit"
            disabled
          >
            Submit
          </Button>
        :
          <Button
            type="primary"
            size="large"
            onClick={props.onClick}
            htmlType="submit"
          >
            Submit
          </Button>
      }
    </Form.Item>
  );
}

export default UploadSubmitButton;