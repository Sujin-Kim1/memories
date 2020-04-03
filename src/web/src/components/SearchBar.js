import React, { Component } from 'react'
import { Col, Row } from 'antd'
import SearchBarInput from './SearchBarInput'
import SearchBarPlaceSelect from './SearchBarPlaceSelect'
import SearchBarSubmitButton from './SearchBarSubmitButton'
import SearchBarYearSelect from './SearchBarYearSelect'

export default class SearchBar extends Component {
  constructor(props) {
    super(props);
    this.state = {
      title : '',
      url : "/search/",
      dateFrom : '',
      dateTo : '',
      location : ''
    }
    this.onChangeTitle = this.onChangeTitle.bind(this)
    this.onChangeLocation = this.onChangeLocation.bind(this)
    this.onChangeDate = this.onChangeDate.bind(this)
  }
  onChangeTitle = (e) => {
    this.setState({
      title : e.target.value
    })
  }
  onChangeLocation (value) {
    this.setState({
      location : value[0] + " "  + value[1] + " " + value[2]
    })
  }
  onChangeDate (value) {
    this.setState({
      dateFrom : value[0]._d.getFullYear(),
      dateTo : value[1]._d.getFullYear()
    })
  }
  render() {
    return (
      <Col span={21} push={5}>
        <Row gutter={[1,1]}>
          <SearchBarInput onChangeTitle={this.onChangeTitle}/>
          <SearchBarPlaceSelect onChangeLocation={this.onChangeLocation}/>
          <SearchBarYearSelect onChangeDate={this.onChangeDate}/>
          <SearchBarSubmitButton title={this.state.title} url={this.state.url} location={this.state.location} dateFrom={this.state.dateFrom} dateTo={this.state.dateTo}/>
        </Row>
      </Col>
    )
  }
}