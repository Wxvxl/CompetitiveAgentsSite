'use client';
import { useState } from 'react';
import {
    LoginOutlined,
    UserOutlined,
    LockOutlined,
    MailOutlined,
    SchoolOutlined,
    TeamOutlined
} from '@ant-design/icons';
import {
    Button,
    Checkbox,
    Form,
    Input,
    Card,
    Tabs,
    Typography,
    Layout,
    Divider,
    message
} from 'antd';
import Link from 'next/link';
import Image from 'next/image';

const { Title, Text } = Typography;
const { TabPane } = Tabs;
const { Header, Content, Footer } = Layout;

const Login = () => {
    const [form] = Form.useForm();
    const [loading, setLoading] = useState(false);

    // 处理登录提交
    const handleLogin = async (values: any) => {
        setLoading(true);
        try {
            // 模拟登录请求
            console.log('登录信息:', {
                identity: values.identity,
                username: values.username,
                password: values.password
            });

            // 实际项目中替换为真实API请求
            // const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/login`, {
            //   method: 'POST',
            //   headers: { 'Content-Type': 'application/json' },
            //   body: JSON.stringify(values)
            // });

            message.success('登录成功');
            // 登录成功后跳转逻辑
        } catch (error) {
            message.error('登录失败，请检查账号密码');
            console.error('登录错误:', error);
        } finally {
            setLoading(false);
        }
    };
    const itemsTab = [
        {
            key: 'Student',
            label: (<span>
                <UserOutlined style={{ marginRight: 8 }} />
                Student Client
            </span>),
            children: (
                <Form
                    form={form}
                    name="student_login"
                    layout="vertical"
                    onFinish={handleLogin}
                    initialValues={{ identity: 'student', remember: true }}
                >
                    <Form.Item
                        name="identity"
                        hidden
                    >
                        <Input value="student" />
                    </Form.Item>

                    <Form.Item
                        name="username"
                        label="Student ID"
                        rules={[
                            { required: true, message: 'Please enter your student ID' },
                            //   { pattern: /^\d+$/, message: '学号必须为数字' }
                        ]}
                    >
                        <Input
                            prefix={<UserOutlined className="site-form-item-icon" />}
                            placeholder="Please enter your student ID"
                        />
                    </Form.Item>

                    <Form.Item
                        name="email"
                        label="email"
                        rules={[
                            { required: true, message: 'Please enter your email' },
                            { type: 'email', message: 'Please enter a correct email format' }
                        ]}
                    >
                        <Input
                            prefix={<MailOutlined className="site-form-item-icon" />}
                            placeholder="Please enter your registered email address"
                        />
                    </Form.Item>

                    <Form.Item
                        name="password"
                        label="Password"
                        rules={[{ required: true, message: 'Please enter the password' }]}
                    >
                        <Input.Password
                            prefix={<LockOutlined className="site-form-item-icon" />}
                            placeholder="Please enter the password"
                        />
                    </Form.Item>

                    {/* <Form.Item name="remember" valuePropName="checked">
                    <Checkbox>记住我</Checkbox>
                  </Form.Item> */}

                    <Form.Item>
                        <Button
                            type="primary"
                            htmlType="submit"
                            className="login-form-button"
                            loading={loading}
                            style={{ width: '100%', height: 45, fontSize: 16 }}
                        >
                            LOGIN
                        </Button>
                    </Form.Item>
                </Form>
            )
        },
        {
            key: 'Teacher',
            label: (
                <span>
                    <TeamOutlined style={{ marginRight: 8 }} />
                    Teacher's End
                </span>
            ),
            children: (
                <Form
                    form={form}
                    name="teacher_login"
                    layout="vertical"
                    onFinish={handleLogin}
                    initialValues={{ identity: 'teacher', remember: true }}
                >
                    <Form.Item
                        name="identity"
                        hidden
                    >
                        <Input value="teacher" />
                    </Form.Item>

                    <Form.Item
                        name="username"
                        label="UserName"
                        rules={[
                            { required: true, message: 'Please enter your account' },
                            // { pattern: /^\d+$/, message: '工号必须为数字' }
                        ]}
                    >
                        <Input
                            prefix={<UserOutlined className="site-form-item-icon" />}
                            placeholder="Please enter your account"
                        />
                    </Form.Item>

                    <Form.Item
                        name="password"
                        label="Password"
                        rules={[{ required: true, message: 'Please enter the password' }]}
                    >
                        <Input.Password
                            prefix={<LockOutlined className="site-form-item-icon" />}
                            placeholder="Please enter the password"
                        />
                    </Form.Item>

                    {/* <Form.Item name="remember" valuePropName="checked">
                                        <Checkbox>记住我</Checkbox>
                                    </Form.Item> */}

                    <Form.Item>
                        <Button
                            type="primary"
                            htmlType="submit"
                            className="login-form-button"
                            loading={loading}
                            style={{ width: '100%', height: 45, fontSize: 16 }}
                        >
                            LOGIN
                        </Button>
                    </Form.Item>
                </Form>
            )
        }
    ]

    return (
        <Layout style={{ minHeight: '100vh', background: '#f0f2f5' }}>

            {/* 主要内容区 */}
            <Content style={{
                flex: 1, // 占满剩余空间
                display: 'flex',
                justifyContent: 'center', // 水平居中
                alignItems: 'center', // 垂直居中
                padding: '20px',
                background: '#f0f2f5'
            }}>
                <div style={{ maxWidth: 600, margin: '0 auto' }}>
                    {/* 登录卡片 */}
                    <Card
                        style={{
                            borderRadius: 12,
                            boxShadow: '0 10px 30px rgba(0,0,0,0.1)',
                            overflow: 'hidden'
                        }}
                    >
                        <div style={{ textAlign: 'center', marginBottom: 24 }}>
                            <LoginOutlined style={{ fontSize: 48, color: '#1890ff', marginBottom: 16 }} />
                            <Title level={2} style={{ margin: 0 }}>LOGIN</Title>
                            <Text type="secondary">Please select your identity and enter your account and password</Text>
                        </div>

                        {/* 身份切换标签页 */}
                        <Tabs
                            defaultActiveKey="student"
                            style={{ marginBottom: 24 }}
                            size="large"
                            items={itemsTab}
                        >

                        </Tabs>

                        {/* 其他操作链接 */}
                        <div style={{ textAlign: 'center' }}>
                            <Divider>Other Operations</Divider>
                            <div style={{ display: 'flex', justifyContent: 'center', gap: 24 }}>
                                <Link href="/forgot-password" style={{ color: '#1890ff' }}>
                                    Forgot password
                                </Link>
                                <Link href="/register/student" style={{ color: '#1890ff' }}>
                                    Student Registration
                                </Link>
                                <Link href="/contact" style={{ color: '#1890ff' }}>
                                    Contact the administrator
                                </Link>
                            </div>
                        </div>
                    </Card>
                </div>
            </Content>

            {/* 页脚 */}
            <Footer style={{ textAlign: 'center' }}>
                ©{new Date().getFullYear()} Created with Ant Design
            </Footer>
        </Layout>
    );
};

export default Login;
